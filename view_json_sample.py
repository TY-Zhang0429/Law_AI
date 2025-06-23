# 文件：view_json_sample.py
import json
import sys
import os
from tqdm import tqdm

def view_json_sample(file_path, sample_size=2):
    """查看JSON文件的前N条记录"""
    if not os.path.exists(file_path):
        print(f"错误：文件不存在 - {file_path}")
        return
    
    print(f"\n{'='*50}")
    print(f"查看文件: {file_path}")
    print(f"样本大小: {sample_size} 条记录")
    print(f"{'='*50}\n")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            # 尝试解析文件结构
            first_char = f.read(1)
            f.seek(0)
            
            if first_char == '[':
                # 数组格式的JSON文件
                print("文件格式: JSON数组")
                records = []
                f.read(1)  # 跳过开头的'['
                
                # 使用简单状态机解析JSON数组
                for i in range(sample_size):
                    record = ""
                    brace_count = 0
                    in_string = False
                    escape = False
                    
                    while True:
                        c = f.read(1)
                        if not c:
                            break
                            
                        if c == '"' and not escape:
                            in_string = not in_string
                        elif c == '\\' and in_string:
                            escape = not escape
                        else:
                            escape = False
                        
                        if not in_string:
                            if c == '{':
                                brace_count += 1
                            elif c == '}':
                                brace_count -= 1
                        
                        record += c
                        
                        if brace_count == 0 and not in_string and c in [',', ']']:
                            break
                    
                    if record.endswith(','):
                        record = record[:-1]
                    
                    if record:
                        try:
                            record_json = json.loads(record)
                            records.append(record_json)
                        except json.JSONDecodeError:
                            print(f"警告: 无法解析记录 {i+1}")
            
            elif first_char == '{':
                # 对象格式的JSON文件
                print("文件格式: JSON对象")
                data = json.load(f)
                
                # 尝试找到包含记录的键
                record_key = None
                for key in ['data', 'results', 'cases', 'documents']:
                    if key in data and isinstance(data[key], list):
                        record_key = key
                        break
                
                if record_key:
                    records = data[record_key][:sample_size]
                    print(f"找到记录键: '{record_key}'")
                else:
                    # 如果不是标准结构，直接展示整个对象
                    records = [data]
            else:
                print("错误: 未知的JSON格式")
                return
                
            # 打印样本记录
            print("\n样本记录:")
            for i, record in enumerate(records, 1):
                print(f"\n记录 #{i}:")
                print(json.dumps(record, ensure_ascii=False, indent=2))
                
    except Exception as e:
        print(f"处理文件时出错: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使用方法: python view_json_sample.py <json文件路径> [样本大小]")
        sys.exit(1)
    
    file_path = sys.argv[1]
    sample_size = int(sys.argv[2]) if len(sys.argv) > 2 else 2
    
    view_json_sample(file_path, sample_size)