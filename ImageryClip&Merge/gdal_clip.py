import gdal

# 读取要切的原图
in_ds = gdal.Open("/data/110515YN1.tiff")
print("open tif file succeed")

# 读取原图中的每个波段
in_band1 = in_ds.GetRasterBand(1)
in_band2 = in_ds.GetRasterBand(2)
in_band3 = in_ds.GetRasterBand(3)
in_band4 = in_ds.GetRasterBand(4)

# image = in_band1.ReadAsArray() #<class 'tuple'>: (88576, 194304)
shape = (88576, 194304)

target_size = 10000

patchs = []
for row_begin in range(0, shape[0],target_size):
    for col_begin in range(0, shape[1],target_size):
        row_end = row_begin + target_size
        col_end = col_begin + target_size
        if row_end > shape[0]:
            row_end = shape[0]
            # row_begin = row_end - target_size
        if col_end > shape[1]:
            col_end = shape[1]
            # col_begin = col_end - target_size
        patchs.append((row_begin, row_end, col_begin, col_end))
for b in patchs:

    # 定义切图的起始点坐标(相比原点的横坐标和纵坐标偏移量)
    offset_x = b[2]#col_begin  # 这里是随便选取的，可根据自己的实际需要设置
    offset_y = b[0]#row_begin

    # 定义切图的大小（矩形框）
    block_xsize = b[3]-b[2]# target_size  # 行
    block_ysize = b[1]-b[0]# target_size  # 列

    # 从每个波段中切需要的矩形框内的数据(注意读取的矩形框不能超过原图大小)
    out_band1 = in_band1.ReadAsArray(offset_x, offset_y, block_xsize, block_ysize)
    out_band2 = in_band2.ReadAsArray(offset_x, offset_y, block_xsize, block_ysize)
    out_band3 = in_band3.ReadAsArray(offset_x, offset_y, block_xsize, block_ysize)
    out_band4 = in_band4.ReadAsArray(offset_x, offset_y, block_xsize, block_ysize)

    # 获取Tif的驱动，为创建切出来的图文件做准备
    gtif_driver = gdal.GetDriverByName("GTiff")

    path = '/data/Aden/Patches/'+'Aden_'+'_'.join('%s' % i for i in b)+'.tif'

    out_ds = gtif_driver.Create(path, block_xsize, block_ysize, 4, in_band1.DataType)
    print("create new tif file succeed")

    # 获取原图的原点坐标信息
    ori_transform = in_ds.GetGeoTransform()
    if ori_transform:
        print (ori_transform)
        print("Origin = ({}, {})".format(ori_transform[0], ori_transform[3]))
        print("Pixel Size = ({}, {})".format(ori_transform[1], ori_transform[5]))

    # 读取原图仿射变换参数值
    top_left_x = ori_transform[0]  # 左上角x坐标
    w_e_pixel_resolution = ori_transform[1] # 东西方向像素分辨率
    top_left_y = ori_transform[3] # 左上角y坐标
    n_s_pixel_resolution = ori_transform[5] # 南北方向像素分辨率

    # 根据反射变换参数计算新图的原点坐标
    top_left_x = top_left_x + offset_x * w_e_pixel_resolution
    top_left_y = top_left_y + offset_y * n_s_pixel_resolution

    # 将计算后的值组装为一个元组，以方便设置
    dst_transform = (top_left_x, ori_transform[1], ori_transform[2], top_left_y, ori_transform[4], ori_transform[5])

    # 设置裁剪出来图的原点坐标
    out_ds.SetGeoTransform(dst_transform)

    # 设置SRS属性（投影信息）
    out_ds.SetProjection(in_ds.GetProjection())

    # 写入目标文件
    out_ds.GetRasterBand(1).WriteArray(out_band1)
    out_ds.GetRasterBand(2).WriteArray(out_band2)
    out_ds.GetRasterBand(3).WriteArray(out_band3)
    out_ds.GetRasterBand(4).WriteArray(out_band4)
    # 将缓存写入磁盘
    out_ds.FlushCache()
    print("FlushCache succeed")


del out_ds

print("End!")


