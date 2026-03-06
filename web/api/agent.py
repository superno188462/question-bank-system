"""
AI Agent API 接口
提供题目提取、解析生成、智能问答、配置管理等功能
"""
import os
import tempfile
import shutil
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Body
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from core.models import (
    StagingQuestion, StagingQuestionCreate, StagingQuestionUpdate,
    ExtractResponse, ExplanationGenerateRequest, ExplanationGenerateResponse,
    QAAskRequest, QAAskResponse, SuccessResponse, ErrorResponse, ErrorCodes
)
from core.database.repositories import StagingQuestionRepository, QALogRepository
from agent.config import AgentConfig
from agent.extractors.image_extractor import ImageExtractor
from agent.extractors.document_extractor import DocumentExtractor
from agent.generators.explanation_generator import ExplanationGenerator

router = APIRouter(prefix="/agent", tags=["AI Agent"])


# ========== 配置管理模型 ==========

class AgentConfigUpdate(BaseModel):
    """配置更新请求模型"""
    llm: Optional[Dict[str, str]] = None
    vision: Optional[Dict[str, str]] = None
    embedding: Optional[Dict[str, str]] = None
    settings: Optional[Dict[str, Any]] = None
    allowed_extensions: Optional[Dict[str, List[str]]] = None


# ========== 题目提取功能 ==========

@router.post("/extract/image")
async def extract_from_image(files: List[UploadFile] = File(...)):
    """
    从图片中提取题目
    
    - 支持多张图片批量上传
    - 自动识别题目并保存到预备题目
    - 返回提取结果
    """
    try:
        # 验证配置
        AgentConfig.validate()
        
        # 保存上传的文件
        temp_dir = tempfile.mkdtemp()
        image_paths = []
        
        try:
            for file in files:
                # 验证文件类型
                ext = file.filename.split('.')[-1].lower()
                if ext not in AgentConfig.ALLOWED_IMAGE_EXTENSIONS:
                    raise HTTPException(
                        status_code=400,
                        detail=f"不支持的图片格式：{ext}"
                    )
                
                # 保存文件
                file_path = os.path.join(temp_dir, file.filename)
                with open(file_path, "wb") as f:
                    content = await file.read()
                    f.write(content)
                image_paths.append(file_path)
            
            # 提取题目
            extractor = ImageExtractor()
            
            if len(image_paths) == 1:
                result = extractor.extract(image_paths[0])
            else:
                result = extractor.extract_batch(image_paths)
            
            extractor.close()
            
            # 保存到预备题目
            saved_questions = []
            if result.get("questions"):
                for q_data in result["questions"]:
                    q_data['source_type'] = result.get('source_type', 'image')
                    q_data['source_file'] = result.get('source_file', file.filename if len(files) == 1 else 'batch')
                    
                    q_id = StagingQuestionRepository.create(q_data)
                    saved_questions.append(StagingQuestion(
                        id=q_id,
                        **q_data
                    ))
            
            return SuccessResponse(
                success=True,
                data={
                    "questions": saved_questions,
                    "total_count": len(saved_questions),
                    "source_type": result.get("source_type", "image"),
                    "source_files": result.get("source_files", [f.filename for f in files]),
                    "confidence": result.get("confidence", result.get("average_confidence", 0)),
                    "error": result.get("error")
                },
                message=f"成功提取 {len(saved_questions)} 道题目"
            )
            
        finally:
            # 清理临时文件
            shutil.rmtree(temp_dir, ignore_errors=True)
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"提取失败：{str(e)}"
        )


@router.post("/extract/document")
async def extract_from_document(files: List[UploadFile] = File(...)):
    """
    从文档中提取题目
    
    - 支持 PDF、Word、TXT、Markdown 格式
    - 自动识别题目并保存到预备题目
    """
    try:
        AgentConfig.validate()
        
        temp_dir = tempfile.mkdtemp()
        document_paths = []
        
        try:
            for file in files:
                ext = file.filename.split('.')[-1].lower()
                if ext not in AgentConfig.ALLOWED_DOCUMENT_EXTENSIONS:
                    raise HTTPException(
                        status_code=400,
                        detail=f"不支持的文档格式：{ext}"
                    )
                
                file_path = os.path.join(temp_dir, file.filename)
                with open(file_path, "wb") as f:
                    content = await file.read()
                    f.write(content)
                document_paths.append(file_path)
            
            extractor = DocumentExtractor()
            
            all_questions = []
            for doc_path in document_paths:
                result = extractor.extract(doc_path)
                if result.get("questions"):
                    all_questions.extend(result["questions"])
            
            extractor.close()
            
            # 保存到预备题目
            saved_questions = []
            for q_data in all_questions:
                q_data['source_type'] = 'document'
                q_data['source_file'] = os.path.basename(doc_path)
                
                q_id = StagingQuestionRepository.create(q_data)
                saved_questions.append(StagingQuestion(
                    id=q_id,
                    **q_data
                ))
            
            return SuccessResponse(
                success=True,
                data={
                    "questions": saved_questions,
                    "total_count": len(saved_questions),
                    "source_type": "document",
                    "source_files": [f.filename for f in files],
                },
                message=f"成功提取 {len(saved_questions)} 道题目"
            )
            
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"提取失败：{str(e)}"
        )


# ========== 预备题目管理 ==========

@router.get("/staging")
async def get_staging_questions(
    status: Optional[str] = None,
    page: int = 1,
    limit: int = 20
):
    """获取预备题目列表"""
    try:
        offset = (page - 1) * limit
        questions = StagingQuestionRepository.get_all(status=status, limit=limit, offset=offset)
        total = StagingQuestionRepository.get_count(status=status)
        
        return SuccessResponse(
            success=True,
            data={
                "questions": questions,
                "total": total,
                "page": page,
                "limit": limit,
                "pages": (total + limit - 1) // limit
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/staging/{question_id}")
async def get_staging_question(question_id: int):
    """获取单个预备题目"""
    question = StagingQuestionRepository.get_by_id(question_id)
    
    if not question:
        raise HTTPException(status_code=404, detail="题目不存在")
    
    return SuccessResponse(success=True, data=question)


@router.put("/staging/{question_id}")
async def update_staging_question(question_id: int, update_data: StagingQuestionUpdate):
    """更新预备题目"""
    question = StagingQuestionRepository.get_by_id(question_id)
    
    if not question:
        raise HTTPException(status_code=404, detail="题目不存在")
    
    update_dict = update_data.dict(exclude_unset=True)
    StagingQuestionRepository.update(question_id, update_dict)
    
    updated = StagingQuestionRepository.get_by_id(question_id)
    return SuccessResponse(success=True, data=updated, message="更新成功")


@router.post("/staging/{question_id}/approve")
async def approve_staging_question(question_id: int, reviewed_by: str = Form("system")):
    """审核通过预备题目"""
    question = StagingQuestionRepository.get_by_id(question_id)
    
    if not question:
        raise HTTPException(status_code=404, detail="题目不存在")
    
    StagingQuestionRepository.approve(question_id, reviewed_by)
    return SuccessResponse(success=True, message="审核通过")


@router.post("/staging/{question_id}/reject")
async def reject_staging_question(question_id: int, reviewed_by: str = Form("system")):
    """审核拒绝预备题目"""
    question = StagingQuestionRepository.get_by_id(question_id)
    
    if not question:
        raise HTTPException(status_code=404, detail="题目不存在")
    
    StagingQuestionRepository.reject(question_id, reviewed_by)
    return SuccessResponse(success=True, message="已拒绝")


@router.delete("/staging/{question_id}")
async def delete_staging_question(question_id: int):
    """删除预备题目"""
    question = StagingQuestionRepository.get_by_id(question_id)
    
    if not question:
        raise HTTPException(status_code=404, detail="题目不存在")
    
    StagingQuestionRepository.delete(question_id)
    return SuccessResponse(success=True, message="删除成功")


# ========== 解析生成 ==========

@router.post("/explanation/generate")
async def generate_explanation(request: ExplanationGenerateRequest):
    """生成题目解析"""
    try:
        AgentConfig.validate()
        
        # 获取题目数据
        if request.question_id:
            # 从题库读取
            from core.services import QuestionService
            question_service = QuestionService()
            question = question_service.get_question(request.question_id)
            
            if not question:
                raise HTTPException(status_code=404, detail="题目不存在")
            
            question_data = {
                "id": question.id,
                "type": "single_choice",  # TODO: 需要从题目中获取
                "content": question.content,
                "options": question.options,
                "answer": question.answer
            }
        else:
            # 使用传入的数据
            question_data = {
                "content": request.content,
                "options": request.options,
                "answer": request.answer,
                "type": request.type or "single_choice"
            }
        
        # 生成解析
        generator = ExplanationGenerator()
        result = generator.generate(question_data)
        generator.close()
        
        if result.get("success"):
            return SuccessResponse(
                success=True,
                data={"explanation": result["explanation"]},
                message="解析生成成功"
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=f"生成失败：{result.get('error', '未知错误')}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ========== 智能问答（占位实现） ==========

@router.post("/ask")
async def ask_question(request: QAAskRequest):
    """
    智能问答
    
    - 用户用自然语言提问
    - AI 从题库检索相关题目
    - 综合回答并记录日志
    """
    # TODO: 实现智能问答功能
    # 目前返回占位响应
    
    return SuccessResponse(
        success=True,
        data={
            "answer": "智能问答功能开发中... 该功能将支持：\n1. 自然语言提问\n2. 从题库检索相关题目\n3. AI 综合回答\n4. 记录问答日志",
            "related_questions": [],
            "suggested_question": None
        },
        message="问答功能即将上线"
    )


@router.get("/logs")
async def get_qa_logs(page: int = 1, limit: int = 20):
    """获取问答日志"""
    try:
        offset = (page - 1) * limit
        logs = QALogRepository.get_all(limit=limit, offset=offset)
        
        return SuccessResponse(
            success=True,
            data={
                "logs": logs,
                "page": page,
                "limit": limit
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ========== 配置管理 ==========

@router.get("/config")
async def get_agent_config():
    """
    获取 Agent 配置
    
    - 返回当前配置（API Key 部分掩码）
    - 用于 Web 界面显示
    """
    try:
        config = AgentConfig.get_full_config()
        return SuccessResponse(
            success=True,
            data=config,
            message="配置获取成功"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/config")
async def update_agent_config(config_update: AgentConfigUpdate):
    """
    更新 Agent 配置
    
    - 支持部分更新
    - 立即生效（热更新）
    - 保存到 config/agent.json
    """
    try:
        # 获取当前配置
        current_config = AgentConfig._load_config(force_refresh=True)
        
        # 合并更新
        if config_update.llm:
            current_config.setdefault("llm", {}).update(config_update.llm)
        if config_update.vision:
            current_config.setdefault("vision", {}).update(config_update.vision)
        if config_update.embedding:
            current_config.setdefault("embedding", {}).update(config_update.embedding)
        if config_update.settings:
            current_config.setdefault("settings", {}).update(config_update.settings)
        if config_update.allowed_extensions:
            current_config.setdefault("allowed_extensions", {}).update(config_update.allowed_extensions)
        
        # 保存配置
        if AgentConfig.save_config(current_config):
            # 刷新配置缓存
            AgentConfig.refresh()
            
            return SuccessResponse(
                success=True,
                data=AgentConfig.get_full_config(),
                message="配置更新成功（立即生效）"
            )
        else:
            raise HTTPException(status_code=500, detail="保存配置文件失败")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新配置失败：{str(e)}")


@router.post("/config/test")
async def test_agent_config():
    """
    测试配置是否有效
    
    - 验证 API Key 是否可用
    - 返回测试结果
    """
    try:
        # 验证配置
        if not AgentConfig.LLM_API_KEY:
            return SuccessResponse(
                success=False,
                data={"status": "not_configured"},
                message="LLM API Key 未配置"
            )
        
        if not AgentConfig.VISION_API_KEY:
            return SuccessResponse(
                success=False,
                data={"status": "not_configured"},
                message="视觉模型 API Key 未配置"
            )
        
        # TODO: 实际测试 API 连接
        # 目前只验证配置是否存在
        return SuccessResponse(
            success=True,
            data={
                "status": "configured",
                "llm_model": AgentConfig.LLM_MODEL_ID,
                "vision_model": AgentConfig.VISION_MODEL_ID,
                "base_url": AgentConfig.LLM_BASE_URL
            },
            message="配置有效"
        )
        
    except Exception as e:
        return SuccessResponse(
            success=False,
            data={"status": "error"},
            message=f"测试失败：{str(e)}"
        )
