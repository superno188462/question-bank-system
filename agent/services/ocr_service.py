"""
OCR 服务核心
支持多引擎自动选择（PaddleOCR/Tesseract）
"""
import logging
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class OcrEngine(ABC):
    """OCR 引擎抽象基类"""
    
    @abstractmethod
    def recognize(self, image_path: str) -> str:
        """
        识别图片中的文字
        
        Args:
            image_path: 图片文件路径
        
        Returns:
            识别的文字内容
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """
        检查引擎是否可用
        
        Returns:
            是否可用
        """
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """引擎名称"""
        pass


class PaddleOcrEngine(OcrEngine):
    """PaddleOCR 引擎实现 - 推荐用于中文场景"""
    
    def __init__(self, lang: str = "ch", use_angle_cls: bool = True):
        """
        初始化 PaddleOCR 引擎
        
        Args:
            lang: 识别语言（ch: 中文，en: 英文，japan: 日文等）
            use_angle_cls: 是否使用方向分类器
        """
        self.lang = lang
        self.use_angle_cls = use_angle_cls
        self._ocr = None
        self._initialized = False
    
    def _lazy_init(self):
        """延迟初始化 PaddleOCR（避免不必要的导入开销）"""
        if not self._initialized:
            try:
                from paddleocr import PaddleOCR
                self._ocr = PaddleOCR(
                    use_angle_cls=self.use_angle_cls,
                    lang=self.lang,
                    show_log=False
                )
                self._initialized = True
                logger.info(f"PaddleOCR 引擎初始化成功（语言：{self.lang}）")
            except ImportError as e:
                logger.warning(f"PaddleOCR 未安装：{e}")
                self._initialized = False
            except Exception as e:
                logger.error(f"PaddleOCR 初始化失败：{e}")
                self._initialized = False
    
    @property
    def name(self) -> str:
        return "paddle"
    
    def is_available(self) -> bool:
        """检查 PaddleOCR 是否可用"""
        try:
            from paddleocr import PaddleOCR
            # 尝试创建实例来验证
            test_ocr = PaddleOCR(use_angle_cls=True, lang=self.lang, show_log=False)
            return True
        except ImportError:
            logger.debug("PaddleOCR 引擎不可用：未安装 paddleocr")
            return False
        except Exception as e:
            logger.debug(f"PaddleOCR 引擎不可用：{e}")
            return False
    
    def recognize(self, image_path: str) -> str:
        """
        使用 PaddleOCR 识别图片文字
        
        Args:
            image_path: 图片文件路径
        
        Returns:
            识别的文字内容
        
        Raises:
            RuntimeError: 当引擎未正确初始化时
        """
        self._lazy_init()
        
        if not self._initialized or self._ocr is None:
            raise RuntimeError("PaddleOCR 引擎未正确初始化")
        
        image_path = Path(image_path)
        if not image_path.exists():
            raise FileNotFoundError(f"图片文件不存在：{image_path}")
        
        try:
            # 执行 OCR 识别
            result = self._ocr.ocr(str(image_path), cls=self.use_angle_cls)
            return self._format_result(result)
        except Exception as e:
            logger.error(f"PaddleOCR 识别失败：{e}")
            raise
    
    def _format_result(self, result: List) -> str:
        """
        格式化 OCR 结果
        
        Args:
            result: PaddleOCR 原始结果
        
        Returns:
            格式化后的文字
        """
        if not result or not result[0]:
            return ""
        
        lines = []
        for line in result[0]:
            if line and len(line) >= 2:
                # line 格式：[[坐标], (文字，置信度)] 或 [[坐标], [文字，置信度]]
                text_data = line[1]
                if isinstance(text_data, (tuple, list)) and len(text_data) >= 1:
                    text = text_data[0]
                elif isinstance(text_data, str):
                    text = text_data
                else:
                    continue
                
                if text:
                    lines.append(str(text))
        
        return "\n".join(lines)


class TesseractOcrEngine(OcrEngine):
    """Tesseract OCR 引擎实现 - 备选方案"""
    
    def __init__(self, lang: str = "chi_sim+eng"):
        """
        初始化 Tesseract OCR 引擎
        
        Args:
            lang: 识别语言（chi_sim: 简体中文，eng: 英文）
        """
        self.lang = lang
        self._pytesseract = None
        self._pillow = None
        self._initialized = False
    
    def _lazy_init(self):
        """延迟初始化 Tesseract"""
        if not self._initialized:
            try:
                import pytesseract
                from PIL import Image
                self._pytesseract = pytesseract
                self._pillow = Image
                # 验证 tesseract 是否可用
                self._pytesseract.get_tesseract_version()
                self._initialized = True
                logger.info(f"Tesseract OCR 引擎初始化成功（语言：{self.lang}）")
            except ImportError as e:
                logger.warning(f"Tesseract 依赖未安装：{e}")
                self._initialized = False
            except Exception as e:
                logger.error(f"Tesseract OCR 初始化失败：{e}")
                self._initialized = False
    
    @property
    def name(self) -> str:
        return "tesseract"
    
    def is_available(self) -> bool:
        """检查 Tesseract 是否可用"""
        try:
            import pytesseract
            from PIL import Image
            # 验证 tesseract 版本
            pytesseract.get_tesseract_version()
            return True
        except ImportError:
            logger.debug("Tesseract 引擎不可用：未安装 pytesseract 或 pillow")
            return False
        except Exception as e:
            logger.debug(f"Tesseract 引擎不可用：{e}")
            return False
    
    def recognize(self, image_path: str) -> str:
        """
        使用 Tesseract 识别图片文字
        
        Args:
            image_path: 图片文件路径
        
        Returns:
            识别的文字内容
        
        Raises:
            RuntimeError: 当引擎未正确初始化时
        """
        self._lazy_init()
        
        if not self._initialized or self._pytesseract is None:
            raise RuntimeError("Tesseract OCR 引擎未正确初始化")
        
        image_path = Path(image_path)
        if not image_path.exists():
            raise FileNotFoundError(f"图片文件不存在：{image_path}")
        
        try:
            image = self._pillow.Image.open(str(image_path))
            text = self._pytesseract.image_to_string(image, lang=self.lang)
            return text.strip()
        except Exception as e:
            logger.error(f"Tesseract OCR 识别失败：{e}")
            raise


class OcrService:
    """
    OCR 服务 - 支持多引擎自动选择和降级
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化 OCR 服务
        
        Args:
            config: OCR 配置，包含：
                - engine: 首选引擎（paddle/tesseract）
                - lang: 识别语言
                - fallback_engines: 备选引擎列表
        """
        self.config = config or {}
        self.preferred_engine = self.config.get("engine", "paddle")
        self.lang = self.config.get("lang", "ch")
        self.fallback_engines = self.config.get("fallback_engines", ["tesseract"])
        
        self.engine: Optional[OcrEngine] = None
        self._init_engine()
    
    def _init_engine(self):
        """初始化 OCR 引擎（支持自动降级）"""
        # 尝试首选引擎
        engine = self._create_engine(self.preferred_engine)
        if engine and engine.is_available():
            self.engine = engine
            logger.info(f"OCR 服务使用引擎：{engine.name}")
            return
        
        # 尝试备选引擎
        for fallback in self.fallback_engines:
            engine = self._create_engine(fallback)
            if engine and engine.is_available():
                self.engine = engine
                logger.warning(f"首选引擎不可用，降级到备选引擎：{engine.name}")
                return
        
        # 所有引擎都不可用
        logger.error("没有可用的 OCR 引擎")
        raise RuntimeError(
            "没有可用的 OCR 引擎。请安装 paddleocr 或 pytesseract：\n"
            "  pip install paddleocr paddlepaddle  # 推荐\n"
            "  pip install pytesseract pillow      # 备选"
        )
    
    def _create_engine(self, engine_type: str) -> Optional[OcrEngine]:
        """
        创建 OCR 引擎实例
        
        Args:
            engine_type: 引擎类型（paddle/tesseract）
        
        Returns:
            OCR 引擎实例或 None
        """
        if engine_type == "paddle":
            # 根据语言配置映射
            lang = self.lang
            if lang in ["ch", "chi_sim", "chi_tra"]:
                lang = "ch"
            elif lang in ["en", "eng"]:
                lang = "en"
            return PaddleOcrEngine(lang=lang)
        elif engine_type == "tesseract":
            # 根据语言配置映射
            lang = self.lang
            if lang in ["ch", "chi_sim"]:
                lang = "chi_sim"
            elif lang in ["chi_tra"]:
                lang = "chi_tra"
            elif lang in ["en", "eng"]:
                lang = "eng"
            else:
                lang = "chi_sim+eng"
            return TesseractOcrEngine(lang=lang)
        else:
            logger.warning(f"未知的 OCR 引擎类型：{engine_type}")
            return None
    
    def recognize(self, image_path: str) -> str:
        """
        识别图片中的文字
        
        Args:
            image_path: 图片文件路径
        
        Returns:
            识别的文字内容
        
        Raises:
            RuntimeError: 当没有可用引擎时
            FileNotFoundError: 当图片文件不存在时
        """
        if self.engine is None:
            raise RuntimeError("OCR 引擎未初始化")
        
        return self.engine.recognize(image_path)
    
    def recognize_with_confidence(self, image_path: str) -> Dict[str, Any]:
        """
        识别图片文字并返回置信度信息
        
        Args:
            image_path: 图片文件路径
        
        Returns:
            包含文字和置信度的字典
        """
        try:
            text = self.recognize(image_path)
            # 简单的置信度估算：基于文字长度和非空行数
            lines = [l for l in text.split('\n') if l.strip()]
            confidence = min(1.0, len(lines) * 0.1 + len(text) * 0.001) if text else 0.0
            
            return {
                "text": text,
                "confidence": confidence,
                "engine": self.engine.name if self.engine else "unknown",
                "line_count": len(lines),
                "char_count": len(text)
            }
        except Exception as e:
            logger.error(f"OCR 识别失败：{e}")
            return {
                "text": "",
                "confidence": 0.0,
                "engine": self.engine.name if self.engine else "unknown",
                "error": str(e)
            }
    
    def is_available(self) -> bool:
        """检查 OCR 服务是否可用"""
        return self.engine is not None and self.engine.is_available()
    
    @property
    def current_engine(self) -> Optional[str]:
        """当前使用的引擎名称"""
        return self.engine.name if self.engine else None
    
    def close(self):
        """关闭 OCR 服务（释放资源）"""
        # PaddleOCR 和 Tesseract 不需要显式关闭
        pass
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
