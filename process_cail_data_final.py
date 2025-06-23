# 文件：process_cail_data_final.py
import os
import json
import logging
from tqdm import tqdm

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("process.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def process_case_entry(case_entry):
    """处理单个案件条目"""
    try:
        # 提取关键信息
        fact_text = case_entry.get("fact", "").replace("\r\n", " ").strip()
        
        # 从meta中提取信息
        meta = case_entry.get("meta", {})
        criminals = meta.get("criminals", [])
        accusation = meta.get("accusation", [])
        articles = meta.get("relevant_articles", [])
        
        # 刑期信息
        imprisonment_info = meta.get("term_of_imprisonment", {})
        imprisonment_months = imprisonment_info.get("imprisonment", 0)
        
        # 创建完整文本（用于向量化）
        full_text = f"案件事实：{fact_text}\n"
        full_text += f"被告人：{', '.join(criminals)}\n"
        full_text += f"罪名：{', '.join(accusation)}\n"
        full_text += f"相关法条：{', '.join(articles)}\n"
        
        # 刑期信息（如果有）
        if imprisonment_months > 0:
            years = imprisonment_months // 12
            months = imprisonment_months % 12
            full_text += f"刑期：{years}年{months}个月" if years > 0 else f"刑期：{months}个月"
        
        return {
            "id": case_entry.get("id", ""),
            "case_id": case_entry.get("case_id", ""),
            "fact": fact_text,
            "criminals": criminals,
            "accusation": accusation,
            "articles": articles,
            "imprisonment": imprisonment_months,
            "punish_of_money": meta.get("punish_of_money", 0),
            "full_text": full_text.strip()
        }
    except Exception as e:
        logger.error(f"处理案件条目时出错: {str(e)}")
        return None

def process_data_file(file_path):
    """处理单个数据文件"""
    processed_cases = []
    try:
        # 获取文件总行数（用于进度条）
        total_lines = sum(1 for _ in open(file_path, 'r', encoding='utf-8'))
        
        with open(file_path, 'r', encoding='utf-8') as f:
            logger.info(f"开始处理文件: {file_path} (约{total_lines}个案例)")
            
            # 逐行处理
            for line in tqdm(f, total=total_lines, desc=f"处理 {os.path.basename(file_path)}"):
                try:
                    case_entry = json.loads(line)
                    case_info = process_case_entry(case_entry)
                    if case_info:
                        processed_cases.append(case_info)
                except json.JSONDecodeError:
                    logger.warning(f"JSON解析失败: {line[:100]}...")
                except Exception as e:
                    logger.error(f"处理行时出错: {str(e)}")
                    
        return processed_cases
    except Exception as e:
        logger.error(f"打开文件 {file_path} 时出错: {str(e)}")
        return []

def process_dataset(dataset_root):
    """处理整个数据集"""
    all_processed_cases = []
    
    # 定义要处理的文件列表
    data_files = [
        # first_stage 目录
        os.path.join(dataset_root, "first_stage", "train.json"),
        os.path.join(dataset_root, "first_stage", "test.json"),
        
        # restData 目录
        os.path.join(dataset_root, "restData", "rest_data.json"),
        
        # 根目录文件
        os.path.join(dataset_root, "final_test.json"),
        
        # exercise_contest 目录（可选）
        os.path.join(dataset_root, "exercise_contest", "data_train.json"),
        os.path.join(dataset_root, "exercise_contest", "data_test.json"),
        os.path.join(dataset_root, "exercise_contest", "data_valid.json")
    ]
    
    # 处理每个文件
    for file_path in data_files:
        if not os.path.exists(file_path):
            logger.warning(f"文件不存在: {file_path}")
            continue
            
        processed_cases = process_data_file(file_path)
        all_processed_cases.extend(processed_cases)
        logger.info(f"已处理 {len(processed_cases)} 个案件，累计 {len(all_processed_cases)} 个案件")
    
    return all_processed_cases

# 主处理流程
if __name__ == "__main__":
    # 设置数据集路径（根据您的实际位置）
    dataset_root = "cail2018_data/final_all_data"
    output_file = "knowledge_base/processed_cases.json"
    
    # 创建输出目录
    os.makedirs("knowledge_base", exist_ok=True)
    
    # 处理数据集
    logger.info("开始处理CAIL2018数据集...")
    all_cases = process_dataset(dataset_root)
    
    # 保存处理后的数据
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_cases, f, ensure_ascii=False, indent=2)
        
    logger.info(f"✅ 处理完成！共处理 {len(all_cases)} 个案件")
    logger.info(f"处理后的数据已保存至 {output_file}")