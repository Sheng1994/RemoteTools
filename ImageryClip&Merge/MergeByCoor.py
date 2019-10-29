import gdal
import numpy as np
import time
import os
from skimage import io
import PIL.Image as Image
# from tqdm import tqdm

Image.MAX_IMAGE_PIXELS = 42949672950
def extractcoor(name):
    coor = name.split('_')[1:5]
    return  coor


def getRbCb(path):
    namelist = os.listdir(path)
    ###(row_begin, row_end, col_begin, col_end)
    coors = list(map(extractcoor,namelist))

    row_begin = []
    col_begin = []

    for c in coors:
        row_begin.append(int(c[0]))
        col_begin.append(int(c[2]))

    row_begin=sorted(set(row_begin))
    col_begin=sorted(set(col_begin))

    return row_begin,col_begin

if __name__ == '__main__':
    path = '/data/RemoteTools/patches2_out'
    row_begin,col_begin = getRbCb(path)

    namelist = os.listdir(path)

    lenr = len(row_begin[:-1])
    lenc = len(col_begin[:-1])

    namearr =np.zeros([lenr,lenc],dtype=np.object)

    for i,rb in enumerate(row_begin[:-1]):
        for j,cb in enumerate(col_begin[:-1]):
            for name in namelist:
                if int(name.split('_')[1]) == rb and int(name.split('_')[3]) == cb :
                    namearr[i,j] = name


    IMAGE_SIZE = 2048  # 每张小图片的大小
    IMAGE_ROW = lenr  # 图片间隔，也就是合并成一张图后，一共有几行
    IMAGE_COLUMN = lenc  # 图片间隔，也就是合并成一张图后，一共有几列
    IMAGES_PATH = '/data/RemoteTools/patches2_out'
    IMAGE_SAVE_PATH = '/data/RemoteTools/0624_merge.tif'
    # 简单的对于参数的设定和实际图片集的大小进行数量判断
    if namearr.size != IMAGE_ROW * IMAGE_COLUMN:
        raise ValueError("合成图片的参数和要求的数量不能匹配！")

    # 定义图像拼接函数
    to_image = Image.new('RGB', (IMAGE_COLUMN * IMAGE_SIZE, IMAGE_ROW * IMAGE_SIZE))  # 创建一个新图
    # 循环遍历，把每张图片按顺序粘贴到对应位置上
    for y in range(0, IMAGE_ROW):
        for x in range(0, IMAGE_COLUMN):
            imgpth = os.path.join(IMAGES_PATH,namearr[y,x])
            from_image = Image.open(imgpth)
            to_image.paste(from_image, (x * IMAGE_SIZE, y* IMAGE_SIZE))
    # to_image.save(IMAGE_SAVE_PATH)  # 保存新图
    all = np.array(to_image,np.uint8)

    in_ds = gdal.Open("/data/RemoteTools/0624_clip.tif")
    gtif_driver = gdal.GetDriverByName("GTiff")
    out_ds = gtif_driver.Create('0624Merge.tif', all.shape[1], all.shape[0], 3)
    print("create new tif file succeed")

    ori_transform = in_ds.GetGeoTransform()
    if ori_transform:
        print(ori_transform)
        print("Origin = ({}, {})".format(ori_transform[0], ori_transform[3]))
        print("Pixel Size = ({}, {})".format(ori_transform[1], ori_transform[5]))

    # 设置裁剪出来图的原点坐标
    out_ds.SetGeoTransform(in_ds.GetGeoTransform())

    # 设置SRS属性（投影信息）
    out_ds.SetProjection(in_ds.GetProjection())

    # 写入目标文件
    out_ds.GetRasterBand(1).WriteArray(all[:,:,0])
    out_ds.GetRasterBand(2).WriteArray(all[:,:,1])
    out_ds.GetRasterBand(3).WriteArray(all[:,:,2])
    # 将缓存写入磁盘
    out_ds.FlushCache()
    print("FlushCache succeed")
    print("End!")