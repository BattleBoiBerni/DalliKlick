import os
import random
import sys
import tkinter
from tkinter import filedialog

from PIL import Image, ImageTk


IMAGE_FORMATS = [
    ".png",
    ".jpg",
    ".jpeg",
    ".tiff",
    ".bmp",
    ".gif",
    ".webp"
]


class Rectangle:
    def __init__(self, canvasID: int, coordinates: tuple[float, float, float, float], position: str) -> None:
        self.CanvasID = canvasID
        self.Coordinates = coordinates
        self.Position = position


class DalliKlick:
    def __init__(self, pictureList: list[str]) -> None:
        self.MainWindow = tkinter.Tk()
        self.SecondWindow = tkinter.Toplevel(self.MainWindow)

        self.BaseSize = self.MainWindow.winfo_screenheight() // 100

        self.HiddenX = 70 * self.BaseSize
        self.HiddenY = 40 * self.BaseSize

        self.PreviewX = 35 * self.BaseSize
        self.PreviewY = 35 * self.BaseSize
        self.ButtonsY = 14 * self.BaseSize

        self.Pictures = pictureList
        self.ImagePointer = 0

        self.RectanglesX = 6
        self.RectanglesY = 6

        self.TempRectanglesX = 6
        self.TempRectanglesY = 6

        self.isPressed = False
        self.OpenPerSecond = 25
        self.AfterID = ""

        self.CurrentDisplayedImage = 0
        self.Rectangles: list[Rectangle] = []

        self.MainWindow.bind("<Configure>", self.ResizeWindow)
        self.MainWindow.bind("<Button-1>", self.KillClickedRectangle)
        self.SecondWindow.bind("<Destroy>", lambda L: self.MainWindow.destroy())

        self.MainWindow.title("Dalli Klick")
        self.SecondWindow.title("Kontrolfenster")

        self.MainWindow.geometry(f"{self.HiddenX}x{self.HiddenY}")
        self.SecondWindow.geometry(
            f"{self.PreviewX}x{self.PreviewY + self.ButtonsY}")
        self.SecondWindow.resizable(False, False)

        self.Canvas = tkinter.Canvas(self.MainWindow, borderwidth=0, background="#000000")
        self.Canvas.pack(fill=tkinter.BOTH, expand=tkinter.YES)

        self.Preview = tkinter.Canvas(self.SecondWindow, borderwidth=0, background="#000000")
        self.Preview.place(x=0, y=0, width=self.PreviewX, height=self.PreviewY)

        self.Name = tkinter.Label(self.SecondWindow, text="Keine Bilder geladen", font=("Helvetica", int(1.25 * self.BaseSize)))
        self.Name.place(x=0, y=self.PreviewY, width=self.PreviewX, height=(3 * self.BaseSize))
        self.Name.bind("<ButtonRelease-1>", lambda event: self.FileDialog())

        self.PreviousButton = tkinter.Button(self.SecondWindow, text="Vorheriges Bild", font=("Helvetica", int(0.75 * self.BaseSize)), command=self.PreviousImage)
        self.PreviousButton.place(x=(2 * self.BaseSize), y=self.PreviewY + (3 * self.BaseSize), width=(9 * self.BaseSize), height=(3 * self.BaseSize))

        self.ShuffleButton = tkinter.Button(self.SecondWindow, text="Bilder mischen", font=("Helvetica", int(0.75 * self.BaseSize)), command=self.ShuffleImages)
        self.ShuffleButton.place(x=(13 * self.BaseSize), y=self.PreviewY + (3 * self.BaseSize), width=(9 * self.BaseSize), height=(3 * self.BaseSize))

        self.NextButton = tkinter.Button(self.SecondWindow, text="Nächstes Bild", font=("Helvetica", int(0.75 * self.BaseSize)), command=self.NextImage)
        self.NextButton.place(x=(24 * self.BaseSize), y=self.PreviewY + (3 * self.BaseSize), width=(9 * self.BaseSize), height=(3 * self.BaseSize))

        self.OpenButton = tkinter.Button(self.SecondWindow, text="Aufdecken", font=("Helvetica", int(0.75 * self.BaseSize)), command=self.KillRandomRectangle)
        self.OpenButton.place(x=(13 * self.BaseSize), y=self.PreviewY + (6.5 * self.BaseSize), width=(9 * self.BaseSize), height=(3 * self.BaseSize))
        self.OpenButton.bind("<ButtonPress-1>", lambda event: self.OpenPressed(True))
        self.OpenButton.bind("<ButtonRelease-1>", lambda event: self.OpenPressed(False))

        self.FinishedButton = tkinter.Button(self.SecondWindow, text="Fertig", font=("Helvetica", int(0.75 * self.BaseSize)), command=self.KillAllRectangles)
        self.FinishedButton.place(x=(13 * self.BaseSize), y=self.PreviewY + (10 * self.BaseSize), width=(9 * self.BaseSize), height=(3 * self.BaseSize))

        self.SliderX = tkinter.Scale(self.SecondWindow, from_=1, to=50, orient=tkinter.HORIZONTAL, label="X-Kästchen", font=("Helvetica", int(0.75 * self.BaseSize)))
        self.SliderX.place(x=(2 * self.BaseSize), y=self.PreviewY + (9 * self.BaseSize), width=(9 * self.BaseSize), height=(8 * self.BaseSize))
        self.SliderX.set(self.RectanglesX)
        self.SliderX.bind("<ButtonRelease-1>", lambda event: self.UpdateTemp())

        self.SliderY = tkinter.Scale(self.SecondWindow, from_=1, to=50, orient=tkinter.HORIZONTAL, label="Y-Kästchen", font=("Helvetica", int(0.75 * self.BaseSize)))
        self.SliderY.place(x=(24 * self.BaseSize), y=self.PreviewY + (9 * self.BaseSize), width=(9 * self.BaseSize), height=(8 * self.BaseSize))
        self.SliderY.set(self.RectanglesY)
        self.SliderY.bind("<ButtonRelease-1>", lambda event: self.UpdateTemp())

        self.Draw()

        self.MainWindow.mainloop()

    def FileDialog(self):
        files = filedialog.askopenfilenames(filetypes=(("All files", "*.*"), ))
        filteredFiles: list[str] = []

        for file in files:
            for format in IMAGE_FORMATS:
                if file.lower().endswith(format) and os.path.isfile(file):
                    filteredFiles.append(file)
                    break

        if filteredFiles:
            self.Pictures.clear()
            self.Pictures.extend(filteredFiles)

    def OpenPressed(self, state: bool) -> None:
        self.isPressed = state
        if self.isPressed:
            self.AfterID = self.MainWindow.after(500, self.OpenContinuesly)
        else:
            self.MainWindow.after_cancel(self.AfterID)

    def OpenContinuesly(self):
        if not self.isPressed:
            return

        self.KillRandomRectangle()
        self.AfterID = self.MainWindow.after((1000 // self.OpenPerSecond), self.OpenContinuesly)

    def UpdateTemp(self):
        self.TempRectanglesX = int(self.SliderX.get())
        self.TempRectanglesY = int(self.SliderY.get())

    def PreviousImage(self) -> None:
        if not self.Pictures:
            return

        self.ImagePointer = (self.ImagePointer - 1) % len(self.Pictures)
        self.Draw()

    def NextImage(self) -> None:
        if not self.Pictures:
            return

        self.ImagePointer = (self.ImagePointer + 1) % len(self.Pictures)
        self.Draw()

    def Draw(self):
        if not self.Pictures:
            return

        self.RectanglesX = self.TempRectanglesX
        self.RectanglesY = self.TempRectanglesY

        self.OpenPerSecond = max(min((self.RectanglesX * self.RectanglesY) // 5, 500), 1)

        self.CurrentOriginalImage = Image.open(self.Pictures[self.ImagePointer])
        self.ImageX = self.CurrentOriginalImage.width
        self.ImageY = self.CurrentOriginalImage.height

        self.Name.configure(text=os.path.basename(self.Pictures[self.ImagePointer]))

        self.CreateImageOnCanvas()
        self.CreateNewRectangles()

    def ShuffleImages(self) -> None:
        random.shuffle(self.Pictures)

    def ResizeWindow(self, event: tkinter.Event) -> None:
        if (event.widget == self.MainWindow):
            if (event.width != self.HiddenX or event.height != self.HiddenY):
                self.HiddenX = event.width
                self.HiddenY = event.height
                self.CreateImageOnCanvas()

    def KillRandomRectangle(self) -> None:
        if self.Rectangles:
            choice = random.randrange(0, len(self.Rectangles))
            self.Canvas.delete(self.Rectangles[choice].CanvasID)
            del self.Rectangles[choice]

    def KillAllRectangles(self) -> None:
        for rectangle in self.Rectangles:
            self.Canvas.delete(rectangle.CanvasID)
        self.Rectangles.clear()

    def KillClickedRectangle(self, event: tkinter.Event):
        for index, rectangle in enumerate(self.Rectangles):
            if ((event.x >= rectangle.Coordinates[0]) and (event.y >= rectangle.Coordinates[1]) and (event.x <= rectangle.Coordinates[2]) and (event.y <= rectangle.Coordinates[3])):
                self.Canvas.delete(rectangle.CanvasID)
                del self.Rectangles[index]
                return

    def CreateImageOnCanvas(self):
        self.Preview.delete("all")

        newImageSize, newImageOffset = self.GetMaxImageSize(self.PreviewX, self.PreviewY)

        self.CurrentPreviewResizedImage = self.CurrentOriginalImage.resize(newImageSize, Image.ANTIALIAS)
        self.CurrentPreviewPhotoImage = ImageTk.PhotoImage(self.CurrentPreviewResizedImage)

        self.Preview.create_image(*newImageOffset, image=self.CurrentPreviewPhotoImage, anchor=tkinter.NW)

        self.Canvas.delete(self.CurrentDisplayedImage)
        for rectangle in self.Rectangles:
            self.Canvas.delete(rectangle.CanvasID)

        newImageSize, newImageOffset = self.GetMaxImageSize()

        self.CurrentResizedImage = self.CurrentOriginalImage.resize(newImageSize, Image.ANTIALIAS)
        self.CurrentPhotoImage = ImageTk.PhotoImage(self.CurrentResizedImage)

        self.CurrentDisplayedImage = self.Canvas.create_image(*newImageOffset, image=self.CurrentPhotoImage, anchor=tkinter.NW)

        sizeOfRectangleX = newImageSize[0] / self.RectanglesX
        sizeOfRectangleY = newImageSize[1] / self.RectanglesY

        oldRectangles = self.Rectangles.copy()
        self.Rectangles.clear()

        for iX in range(self.RectanglesX):
            for iY in range(self.RectanglesY):
                for i in range(len(oldRectangles)):
                    if (f"{iX} {iY}" == oldRectangles[i].Position):
                        del oldRectangles[i]
                        self.CreateSingleRectangle((newImageOffset[0] +
                                                    ((iX + 0) * sizeOfRectangleX)),
                                                   (newImageOffset[1] +
                                                    ((iY + 0) * sizeOfRectangleY)),
                                                   (newImageOffset[0] +
                                                    ((iX + 1) * sizeOfRectangleX)),
                                                   (newImageOffset[1] +
                                                    ((iY + 1) * sizeOfRectangleY)),
                                                   f"{iX} {iY}")
                        break

    def CreateNewRectangles(self):
        for rectangle in self.Rectangles:
            self.Canvas.delete(rectangle.CanvasID)
        self.Rectangles.clear()

        newImageSize, newImageOffset = self.GetMaxImageSize()

        sizeOfRectangleX = newImageSize[0] / self.RectanglesX
        sizeOfRectangleY = newImageSize[1] / self.RectanglesY

        for iX in range(self.RectanglesX):
            for iY in range(self.RectanglesY):
                self.CreateSingleRectangle((newImageOffset[0] +
                                            ((iX + 0) * sizeOfRectangleX)),
                                           (newImageOffset[1] +
                                            ((iY + 0) * sizeOfRectangleY)),
                                           (newImageOffset[0] +
                                            ((iX + 1) * sizeOfRectangleX)),
                                           (newImageOffset[1] +
                                            ((iY + 1) * sizeOfRectangleY)),
                                           f"{iX} {iY}")

    def CreateSingleRectangle(self, X1: float, Y1: float, X2: float, Y2: float, ID: str) -> None:
        coordinate = (X1, Y1, X2, Y2)
        newRectangle = self.Canvas.create_rectangle(coordinate, fill="#000000")

        self.Rectangles.append(Rectangle(newRectangle, coordinate, ID))

    def GetMaxImageSize(self, maxX: int = -1, maxY: int = -1) -> tuple[tuple[int, int], tuple[int, int]]:
        if (maxX < 0 or maxY < 0):
            maxX = self.HiddenX
            maxY = self.HiddenY

        adjustedX = round(self.ImageX / (self.ImageY / maxY))
        adjustedY = round(self.ImageY / (self.ImageX / maxX))

        diffX = adjustedX - maxX
        diffY = adjustedY - maxY

        if (diffX > diffY):
            return ((maxX, adjustedY), (0, round((maxY - adjustedY) / 2)))
        elif (diffX < diffY):
            return ((adjustedX, maxY), (round((maxX - adjustedX) / 2), 0))
        else:
            return ((maxX, maxY), (0, 0))


if __name__ == "__main__":
    pictureList: list[str] = []
    if (len(sys.argv) > 1):
        pictureList.extend(sys.argv[1:])
    else:
        with os.scandir() as files:
            for file in files:
                for format in IMAGE_FORMATS:
                    if file.name.lower().endswith(format) and file.is_file():
                        pictureList.append(file.path)
                        break

    DalliKlick(pictureList)
