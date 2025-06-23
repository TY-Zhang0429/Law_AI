# 文件：view_large_file.py
import os
import sys

def view_file_head(file_path, lines=20):
    """查看大文件的开头部分"""
    if not os.path.exists(file_path):
        print(f"错误：文件不存在 - {file_path}")
        return
    
    print(f"\n查看文件开头: {file_path}")
    print(f"显示前 {lines} 行\n{'='*60}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            # 读取文件开头
            for i in range(lines):
                line = f.readline()
                if not line:
                    break
                print(f"{i+1}: {line.strip()}")
    except Exception as e:
        print(f"处理文件时出错: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使用方法: python view_large_file.py <文件路径> [行数]")
        sys.exit(1)
    
    file_path = sys.argv[1]
    lines = int(sys.argv[2]) if len(sys.argv) > 2 else 20
    
    view_file_head(file_path, lines)