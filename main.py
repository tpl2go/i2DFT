import wx
import wx.grid as gridlib
from sets import Set
import numpy as np
import matplotlib as plt
import matplotlib.figure as pltf
import matplotlib.backends.backend_wxagg as pltb


class LeftPanel(wx.Panel):
    """Child class of wx.Panel"""
    def __init__(self, parent):
        """Child Panel Constructor"""
        wx.Panel.__init__(self, parent)
        self.currentlySelectedCell = (0, 0)

        self.selectedCells = Set()
 
        self.myGrid = gridlib.Grid(self)
        self.myGrid.CreateGrid(40, 40)

        self.myGrid.Bind(gridlib.EVT_GRID_SELECT_CELL, self.onSingleSelect)
        self.myGrid.Bind(gridlib.EVT_GRID_RANGE_SELECT, self.onDragSelection)
 
 
        sizer = wx.BoxSizer(wx.VERTICAL) # orientation of items in sizer
        sizer.Add(self.myGrid, 1, wx.EXPAND)
        self.SetSizer(sizer)

        self.myGrid.DisableCellEditControl()
        self.myGrid.DisableDragColSize()
        self.myGrid.DisableDragRowSize()
        self.myGrid.SetDefaultColSize(1)
        self.myGrid.SetDefaultRowSize(1)
        self.myGrid.HideColLabels()
        self.myGrid.HideRowLabels()
        self.myGrid.EnableEditing(False)
        self.myGrid.SetMargins(0,0)
 
    #----------------------------------------------------------------------
    def onDragSelection(self, event):
        """
        Gets the cells that are selected by holding the left
        mouse button down and dragging
        """
        if self.myGrid.GetSelectionBlockTopLeft():
            top_left = self.myGrid.GetSelectionBlockTopLeft()[0]
            bottom_right = self.myGrid.GetSelectionBlockBottomRight()[0]
            self.colorSelectedCells(top_left, bottom_right)
            self.addSelectedCells(top_left, bottom_right)
 
    #----------------------------------------------------------------------
    def onSingleSelect(self, event):
        """
        Get the selection of a single cell by clicking or 
        moving the selection with the arrow keys
        """
        row = event.GetRow()
        col = event.GetCol()

        self.myGrid.SetCellBackgroundColour(row, col, (0,0,0))
        self.selectedCells.add((row,col))
        event.Skip()


    def colorSelectedCells(self, top_left, bottom_right):
 
        rows_start = top_left[0]
        rows_end = bottom_right[0]
 
        cols_start = top_left[1]
        cols_end = bottom_right[1]
 
        rows = range(rows_start, rows_end+1)
        cols = range(cols_start, cols_end+1)
 
        cells = ([(row, col) for row in rows for col in cols])
 
        for cell in cells:
            row, col = cell
            self.myGrid.SetCellBackgroundColour(row, col, (0,0,0))

    def addSelectedCells(self, top_left, bottom_right):
 
        rows_start = top_left[0]
        rows_end = bottom_right[0]
 
        cols_start = top_left[1]
        cols_end = bottom_right[1]
 
        rows = range(rows_start, rows_end+1)
        cols = range(cols_start, cols_end+1)
 
        cells = ([(row, col) for row in rows for col in cols])
        self.selectedCells |= Set(cells)
 
class RightPanel(wx.Panel):
    """Child class of wx.Panel"""
    def __init__(self, parent, grid):
        wx.Panel.__init__(self, parent,-1,size=(50,50))

        self.leftPanel = grid

        self.figure = pltf.Figure()
        self.axes = self.figure.add_subplot(111)
        t = np.arange(0.0,10,1.0)
        s = [0,1,0,1,0,2,1,2,1,0]
        m = np.random.rand(100,100)
        mft = np.fft.fft2(m)
        self.y_max = 1.0
        self.axes.imshow(np.abs(m))
        self.canvas = pltb.FigureCanvas(self,-1,self.figure)
        self.toolbar = pltb.NavigationToolbar2WxAgg(self.canvas)
        self.toolbar.Hide()

        selectBtn = wx.Button(self, label="Plot FFT")
        selectBtn.Bind(wx.EVT_BUTTON, self.plotFFT)
        sibut = wx.Button(self,-1,label="Zoom")
        sibut.Bind(wx.EVT_BUTTON,self.zoom)
 
        sizer = wx.BoxSizer(wx.VERTICAL) # orientation of items in sizer
        sizer.Add(self.canvas, 1, wx.EXPAND)
        sizer.Add(selectBtn, 0, wx.ALL|wx.CENTER, 5)
        sizer.Add(sibut, 0, wx.ALL|wx.CENTER, 5)
        self.SetSizer(sizer)

    def generateMatrix(self, s):
        m = 10
        M = np.zeros([40*m,40*m])
        for (row,col) in s:
            M[row*m:(row+1)*m,col*m:(col+1)*m] = 1.0
        return M

    def plotFFT(self, event):
        M = self.generateMatrix(self.leftPanel.selectedCells)
        MFFT = np.fft.fft2(M)
        self.axes.imshow(np.fft.fftshift(np.abs(MFFT)))
        self.canvas = pltb.FigureCanvas(self,-1,self.figure)

    def zoom(self, event):
        self.toolbar.zoom() # broken


class MyFrame(wx.Frame):
    """"""
 
    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        wx.Frame.__init__(self, parent=None, title="2D Fourier Transform", size=(2000, 650))
        splitter = wx.SplitterWindow(self)
        leftP = LeftPanel(splitter)
        rightP = RightPanel(splitter, leftP)
 
        # split the window
        splitter.SplitVertically(leftP, rightP,sashPosition=0)
        splitter.SetSashGravity(0.5)

 
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(splitter, 1, wx.EXPAND)
        self.SetSizer(sizer)

        self.Show()
 
#----------------------------------------------------------------------
if __name__ == "__main__":
    app = wx.App(False)
    frame = MyFrame()
    app.MainLoop()
