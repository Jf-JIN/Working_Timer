# Working_Timer

该软件为计时软件，运行软件后会在软件所在的文件夹内生成一个 .WorkingTimer_(Dont_Delete) 的文件，该文件内会记录所有的计时信息，请谨慎修改 软件中的导出excel文件的路径也是软件当前的文件夹 由于用pyinstaller --windowed 打包的，所以windows会报毒。如果有小伙伴知道怎么可以解决这个问题，欢迎讨论。 软件是临时写的，所以结构可能不是很好，还请多多谅解！

This software is a timing tool. After running the software, a file named `.WorkingTimer_(Dont_Delete)` will be generated in the folder where the software is located. This file will record all timing information, so please modify it with caution.

The path for exporting Excel files in the software is also the current folder of the software.

Due to being packaged with `pyinstaller --windowed`, Windows may report it as a virus. If anyone knows how to resolve this issue,  I’d love to hear your thoughts!

The software is a temporary implementation, so the structure may not be very good. Thank you for your understanding!

## 使用方法

1. 当首次运行或内容全部删除时，左侧的运行按钮会隐藏，此时需要先创建分类。
2. 分类创建好后，可以使用手动添加计时记录，也可以立即计时。
3. 当点击开始时，计时器开始计时。此时当软件关闭后，不会终止该计时器计时。原理是计时基于外部文件 `.WorkingTimer_(Dont_Delete)` 的start_timestamp 进行计算的，所以只要该文件仍存在，再次打开软件后，则软件可通过计算得到持续时间。进而显示在屏幕上。
4. 软件支持多计时器，可在多个分类中进行计时。但是如果当前分类已经在计时的话，则无法手动添加计时记录。
5. 每个分类的计时器启动情况，将在分类下拉菜单栏中显示，<span style="background-color: red;">红色表示正在计时</span>，<span style="background-color: green;color:white">绿色表示准备就绪，等待计时</span> 。
6. 如果有程序崩溃的情况，如果可以的话，请将动作/情况/场景告诉我，我将尽快修改bug。



下载链接：https://github.com/Jf-JIN/Working_Timer/releases/tag/Timer

![main](https://github.com/user-attachments/assets/e609a8d9-468f-45d7-828d-08d07ebec77d)

![starting](https://github.com/user-attachments/assets/f8fe66d1-cae4-4dbf-9bde-77e9dce9b2f0)

![end](https://github.com/user-attachments/assets/0f2628df-df94-43e6-9a1c-2a6f73e43edb)

![manual](https://github.com/user-attachments/assets/cab536cf-fc0f-4bef-b642-e037a8aa54c0)

![save_in_excel](https://github.com/user-attachments/assets/13ec1022-99af-44ad-b9af-8217041c3be5)













`