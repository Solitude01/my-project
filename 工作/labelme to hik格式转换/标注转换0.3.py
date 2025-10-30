import json
import os
import glob
import shutil
from pathlib import Path

# 导入新的转换核心模块
try:
    from converter_core import LabelmeConverter, ConversionMode, LabelMapping
    NEW_CORE_AVAILABLE = True
except ImportError:
    NEW_CORE_AVAILABLE = False
    print("注意: 新的转换核心模块不可用，使用传统模式")

def convert_labelme_to_detection_format(input_folder, output_folder):
    """
    批量将labelme格式转换为单检测标注格式，并整理文件结构
    （兼容性函数，调用新的核心模块）
    
    Args:
        input_folder: 输入文件夹路径，包含labelme的json文件和对应图片
        output_folder: 输出文件夹路径
    """
    
    if NEW_CORE_AVAILABLE:
        # 使用新的转换核心
        converter = LabelmeConverter()
        success, message = converter.convert_labelme_to_format(
            input_folder, output_folder, ConversionMode.SINGLE_DETECTION, print
        )
        if not success:
            print(f"转换失败: {message}")
        return
    
    # 原有的转换逻辑（备用）
    # 创建输出文件夹结构
    os.makedirs(output_folder, exist_ok=True)
    result_folder = os.path.join(output_folder, "Result")
    os.makedirs(result_folder, exist_ok=True)
    
    # 获取所有json文件
    json_files = glob.glob(os.path.join(input_folder, "*.json"))
    
    print(f"找到 {len(json_files)} 个标注文件")
    
    # 存储所有转换后的标注数据
    all_frame_infos = []
    
    # 支持的图片格式
    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif']
    
    for json_file in json_files:
        try:
            # 读取labelme格式的json文件
            with open(json_file, 'r', encoding='utf-8') as f:
                labelme_data = json.load(f)
            
            # 提取图片信息
            image_path = labelme_data.get('imagePath', '')
            image_width = labelme_data.get('imageWidth', 0)
            image_height = labelme_data.get('imageHeight', 0)
            shapes = labelme_data.get('shapes', [])
            
            # 查找对应的图片文件
            image_found = False
            json_basename = Path(json_file).stem
            
            # 首先尝试使用labelme中记录的图片路径
            if image_path:
                full_image_path = os.path.join(input_folder, image_path)
                if os.path.exists(full_image_path):
                    image_found = True
                    source_image_path = full_image_path
                    final_image_name = image_path
            
            # 如果没找到，尝试根据json文件名查找同名图片
            if not image_found:
                for ext in image_extensions:
                    potential_image_path = os.path.join(input_folder, json_basename + ext)
                    if os.path.exists(potential_image_path):
                        image_found = True
                        source_image_path = potential_image_path
                        final_image_name = json_basename + ext
                        break
            
            if not image_found:
                print(f"警告: 未找到与 {json_file} 对应的图片文件")
                continue
            
            # 复制图片到输出文件夹
            dest_image_path = os.path.join(output_folder, final_image_name)
            try:
                shutil.copy2(source_image_path, dest_image_path)
                print(f"✓ 复制图片: {final_image_name}")
            except Exception as e:
                print(f"✗ 复制图片失败 {final_image_name}: {str(e)}")
                continue
            
            # 构建目标格式的数据结构
            targets = []
            
            for shape in shapes:
                label = shape.get('label', '')
                points = shape.get('points', [])
                shape_type = shape.get('shape_type', '')
                
                if not points:
                    continue
                
                # 确定目标类型
                target_type = 1 if shape_type == 'rectangle' else 3  # 1-矩形，3-四边形
                
                # 转换坐标为归一化坐标
                vertices = []
                
                if shape_type == 'rectangle' and len(points) == 2:
                    # 矩形：从两个点构建四个顶点
                    x1, y1 = points[0]
                    x2, y2 = points[1]
                    
                    # 确保坐标顺序正确（左上、右上、右下、左下）
                    min_x, max_x = min(x1, x2), max(x1, x2)
                    min_y, max_y = min(y1, y2), max(y1, y2)
                    
                    vertices = [
                        {"fX": min_x / image_width, "fY": min_y / image_height},  # 左上
                        {"fX": max_x / image_width, "fY": min_y / image_height},  # 右上
                        {"fX": max_x / image_width, "fY": max_y / image_height},  # 右下
                        {"fX": min_x / image_width, "fY": max_y / image_height}   # 左下
                    ]
                elif shape_type == 'polygon' and len(points) >= 3:
                    # 多边形：直接使用给定的点
                    for point in points:
                        vertices.append({
                            "fX": point[0] / image_width,
                            "fY": point[1] / image_height
                        })
                    
                    # 如果是四边形，设置target_type为3
                    if len(points) == 4:
                        target_type = 3
                else:
                    print(f"警告: 不支持的形状类型 '{shape_type}' 或点数不正确: {len(points)}")
                    continue
                
                # 构建target对象
                target = {
                    "value": {
                        "TargetType": target_type,
                        "Vertex": vertices,
                        "PropertyPages": [{
                            "PropertyPageDescript": label
                        }]
                    }
                }
                
                targets.append(target)
            
            # 构建frame info对象
            frame_info = {
                "value": {
                    "FrameNum": final_image_name,
                    "mapTargets": targets
                }
            }
            
            all_frame_infos.append(frame_info)
            
            print(f"✓ 处理完成: {json_basename}")
            print(f"  - 图片: {final_image_name}")
            print(f"  - 尺寸: {image_width}x{image_height}")
            print(f"  - 标注数量: {len(targets)}")
            
        except Exception as e:
            print(f"✗ 处理失败 {json_file}: {str(e)}")
    
    # 构建最终的输出格式，将所有标注放在一个json文件中
    if all_frame_infos:
        final_output_data = {
            "calibInfo": {
                "VideoChannels": [{
                    "VideoInfo": {
                        "mapFrameInfos": all_frame_infos
                    }
                }]
            }
        }
        
        # 保存合并后的标注文件到Result文件夹
        output_json_path = os.path.join(result_folder, "merged_annotations.json")
        
        with open(output_json_path, 'w', encoding='utf-8') as f:
            json.dump(final_output_data, f, ensure_ascii=False, indent=2)
        
        print(f"✓ 合并标注文件保存至: {output_json_path}")
        print(f"✓ 总共处理了 {len(all_frame_infos)} 个图片的标注")
    else:
        print("✗ 没有成功处理任何标注文件")

def main():
    """主函数"""
    print("=== labelme格式转单检测格式转换工具 ===")
    print("功能说明:")
    print("- 将输入文件夹中的图片复制到输出文件夹")
    print("- 将所有标注合并到一个json文件，保存在输出文件夹/Result/")
    print()
    
    # 设置输入和输出文件夹路径
    input_folder = input("请输入包含图片和labelme标注文件的文件夹路径: ").strip()
    if not input_folder:
        input_folder = "./input"  # 默认输入文件夹
    
    output_folder = input("请输入输出文件夹路径 (回车使用默认路径 ./output): ").strip()
    if not output_folder:
        output_folder = "./output"  # 默认输出文件夹
    
    # 检查输入文件夹是否存在
    if not os.path.exists(input_folder):
        print(f"错误: 输入文件夹 '{input_folder}' 不存在")
        return
    
    print(f"输入文件夹: {input_folder}")
    print(f"输出文件夹: {output_folder}")
    print(f"标注文件将保存至: {os.path.join(output_folder, 'Result')}")
    print("-" * 50)
    
    # 执行转换
    convert_labelme_to_detection_format(input_folder, output_folder)
    
    print("-" * 50)
    print("转换完成！")
    print("文件结构:")
    print(f"  {output_folder}/")
    print(f"  ├── 图片文件")
    print(f"  └── Result/")
    print(f"      └── merged_annotations.json (合并的标注文件)")

if __name__ == "__main__":
    main()