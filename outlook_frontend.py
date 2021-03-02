import clr
import sys

clr.AddReference("PresentationCore")
clr.AddReference("PresentationFramework")
clr.AddReference("Windowsbase")
clr.AddReferenceByPartialName("IronPython")
clr.AddReference("System.Xml")
clr.AddReference("System.Data")

from System import *
from System.Windows.Controls import *
from System.Windows import *
from System.Windows.Markup import *
from System.Windows.Media import *
from System.IO import *
from System.Windows.Threading import *
import IronPython
from System.Threading import *
from System.Xml import *
from System.Windows.Data import *
from System.Data import *
from System.Windows.Media.Imaging import BitmapImage
from System.Diagnostics import *
from System.Net import *
from System.Text import *

def log(msg):
	Debug.WriteLine(msg)
	print msg

class ScreenLoader:
	def __init__(self):
		self.name = "ScreenLoader"

	def getScreen(self, xamlFile):
		try:
			reader = XamlReader()
			fs = File.OpenRead(xamlFile)
			obj = reader.Load(fs)

			fs.Close()

			return obj
		except Exception, ex:
			print ex

class MaxSizeStack:
	def __init__(self, maxSize):
		self.maxSize = maxSize
		self.items = []

	def push(self, item):
		self.items.append(item)
		if len(self.items) > self.maxSize:
			del self.items[0]
	
	def pop(self):
		return self.items.pop()

	def __len__(self):
		return len(self.items)

	def getList(self):
		return self.items

class AppWindow(Window):
	def __init__(self):
		self.Width = 280 * 5 # 5 inches
		self.Height = 150 * 5 # 5 inches
		self.Title = "ConnectWise Managed Server Log Utility"

		self.screenLoader = ScreenLoader()
		self.Content = self.screenLoader.getScreen("frontend.xaml")
		self.tabs = {0:["log.xaml", self.logSelected]}

		info = FileInfo("logo.png")

		self.Content.FindName("imgLogo").Source = BitmapImage(Uri("file://"+info.DirectoryName+"/logo.png", UriKind.Absolute))
		self.tabControl = self.Content.FindName("tabs")
		self.setupTabs()
		self.logdir = "E:\\github\\log-ui\\logs"
		self.logfile = self.logdir + "\\server.log"
		self.tabIndex = 0

	def setText(self, text):
		if self.tabControl.SelectedIndex != 0:
			return

		self.selectedTab.Content.FindName("txtLog").Text = text
		self.selectedTab.Content.FindName("txtLog").ScrollToEnd()

	def showLogContents(self):
		try:
			stack = MaxSizeStack(30)
			infile = file(self.logfile)
			for line in infile.xreadlines():
				stack.push(line)
			infile.close()
		except Exception, ex:
			print ex.ToString()
			return

		text = ""
		for line in stack.getList():
			text += line

		handler = lambda *args: self.setText(text)
		self.tabControl.Dispatcher.BeginInvoke(DispatcherPriority.Normal, IronPython.Runtime.Calls.CallTarget0(handler))

	def logChanged(self, *args):
		self.showLogContents()

	def logSelected(self, *args):
		watcher = FileSystemWatcher()
		watcher.Path = self.logdir
		watcher.NotifyFilter = NotifyFilters.LastWrite
		watcher.Changed += self.logChanged

		watcher.EnableRaisingEvents = True

		self.showLogContents()
	
	def tabChanged(self, *args):
		self.loadTab(self.tabControl.SelectedIndex)
		self.tabIndex = self.tabControl.SelectedIndex

	def loadTab(self, tabIdx):
		selection = self.tabs[tabIdx]
		obj = self.screenLoader.getScreen(selection[0])
		self.tabControl.SelectedItem.Content = obj
		self.selectedTab = self.tabControl.SelectedItem
		selection[1](obj)

	def setupTabs(self):
		self.tabControl.SelectionChanged += self.tabChanged

def startUp(*args):
	uri = Uri("PresentationFramework.Luna;V3.0.0.0;31bf3856ad364e35;component\\themes/luna.normalcolor.xaml", UriKind.Relative);
	app.Resources.MergedDictionaries.Add(Application.LoadComponent(uri)); 

def certCallback(*args):
	return True

ServicePointManager.ServerCertificateValidationCallback = certCallback

app = Application()
app.Startup += startUp
app.Run(AppWindow())


