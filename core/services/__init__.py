# Core Services Package
# 导出各服务模块中的服务类

from core.services.category_service import CategoryService
from core.services.tag_service import TagService
from core.services.question_service import QuestionService

# SearchService 保留在原 services.py 中（依赖其他服务）
import importlib.util
import os

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
services_path = os.path.join(base_dir, 'services.py')
spec = importlib.util.spec_from_file_location("services_module", services_path)
services_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(services_module)

SearchService = services_module.SearchService

__all__ = ['CategoryService', 'TagService', 'QuestionService', 'SearchService']
