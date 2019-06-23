import gdal
import numpy as np
from skimage import io
import os
from tqdm import tqdm

in_ds = gdal.Open("/data/110515YN1.tiff")
print("open tif file succeed")

cols = in_ds.RasterXSize
rows = in_ds.RasterYSize
bands = in_ds.RasterCount

# image = in_band1.ReadAsArray() #<class 'tuple'>: (88576, 194304)
# shape = (88576, 194304)
# Pre = np.zeros((rows,cols,bands)).astype(np.uint8)

target_size = 10000# target_size = 1024


# 获取Tif的驱动，为创建切出来的图文件做准备
gtif_driver = gdal.GetDriverByName("GTiff")

# 创建切出来的要存的文件（3代表3个波段，最后一个参数为数据类型，跟原文件一致）
out_ds = gtif_driver.Create('Pre.tif', cols,rows, 3)
print("create new tif file succeed")


out_band1 = out_ds.GetRasterBand(1)
out_band2 = out_ds.GetRasterBand(2)
out_band3 = out_ds.GetRasterBand(3)

xBlockSize = target_size
yBlockSize = target_size

# for i in range(0, rows, yBlockSize):
#    if i + yBlockSize < rows:
#         numRows = yBlockSize
#    else:
#         numRows = rows -i
#    for j in range(0, cols, xBlockSize):
#         if j + xBlockSize < cols:
#              numCols = xBlockSize
#         else:
#              numCols = cols -j
#         # data = band.ReadAsArray(j, i, numCols, numRows)
#         # do calculations here to create outData array
#
#         patch_ds = gdal.Open("/data/Aden/Aden110515YN1.tiff")
#         # out1.WriteArray(patch_ds, j, i)
#
#         out_band1.WriteArray(patch_ds.GetRasterBand(1), j, i)
#         out_band2.WriteArray(patch_ds.GetRasterBand(2), j, i)
#         out_band3.WriteArray(patch_ds.GetRasterBand(3), j, i)


# for i in range(0, rows, yBlockSize):
#    if i + yBlockSize < rows:
#         numRows = yBlockSize
#    else:
#         numRows = rows -i
#    for j in range(0, cols, xBlockSize):
#         if j + xBlockSize < cols:
#              numCols = xBlockSize
#         else:
#              numCols = cols -j
        # data = band.ReadAsArray(j, i, numCols, numRows)
        # do calculations here to create outData array

file_dir = '/data/Aden/Patches'
for root, dirs, files in os.walk(file_dir):
    for file in tqdm(files):
        path = os.path.join(root, file)
        row_begin,col_begin=file.split('_')[1], file.split('_')[3]  #(row_begin, row_end, col_begin, col_end)  'Aden_60000_70000_50000_60000.tif'
        patch_ds = gdal.Open(path)
            # out1.WriteArray(patch_ds, j, i)
        # patch_band1 = patch_ds.GetRasterBand(1)
        # patch_band2 = patch_ds.GetRasterBand(2)
        # patch_band3 = patch_ds.GetRasterBand(3)

        out_band1.WriteArray(patch_ds.GetRasterBand(1).ReadAsArray(), int(col_begin), int(row_begin))
        out_band2.WriteArray(patch_ds.GetRasterBand(2).ReadAsArray(), int(col_begin), int(row_begin))
        out_band3.WriteArray(patch_ds.GetRasterBand(3).ReadAsArray(), int(col_begin), int(row_begin))

# 获取原图的原点坐标信息
ori_transform = in_ds.GetGeoTransform()
if ori_transform:
    print (ori_transform)
    print("Origin = ({}, {})".format(ori_transform[0], ori_transform[3]))
    print("Pixel Size = ({}, {})".format(ori_transform[1], ori_transform[5]))

# 读取原图仿射变换参数值
# top_left_x = ori_transform[0]  # 左上角x坐标
# w_e_pixel_resolution = ori_transform[1] # 东西方向像素分辨率
# top_left_y = ori_transform[3] # 左上角y坐标
# n_s_pixel_resolution = ori_transform[5] # 南北方向像素分辨率

# # 根据反射变换参数计算新图的原点坐标
# top_left_x = top_left_x + offset_x * w_e_pixel_resolution
# top_left_y = top_left_y + offset_y * n_s_pixel_resolution

# 将计算后的值组装为一个元组，以方便设置
# dst_transform = (top_left_x, ori_transform[1], ori_transform[2], top_left_y, ori_transform[4], ori_transform[5])

# 设置裁剪出来图的原点坐标
out_ds.SetGeoTransform(in_ds.GetGeoTransform())

# 设置SRS属性（投影信息）
out_ds.SetProjection(in_ds.GetProjection())

# 写入目标文件
out_ds.GetRasterBand(1).WriteArray(out_band1.ReadAsArray())
out_ds.GetRasterBand(2).WriteArray(out_band2.ReadAsArray())
out_ds.GetRasterBand(3).WriteArray(out_band3.ReadAsArray())

# 将缓存写入磁盘
out_ds.FlushCache()
print("FlushCache succeed")

# 计算统计值
# for i in range(1, 3):
#     out_ds.GetRasterBand(i).ComputeStatistics(False)
# print("ComputeStatistics succeed")

del out_ds

print("End!")





