#!/usr/bin/python3
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from interface import Ui_MainWindow
from http.server import HTTPServer, BaseHTTPRequestHandler
from socket import socket, AF_INET, SOCK_DGRAM
import traceback, sys, os

server = None



class WorkerSignals(QObject):
	"""
	Defines the signals available from a running server thread.

	Supported signals are:

	finished
		No data

	error
		tuple (exctype, value, traceback.format_exc() )

	result
		object data returned from processing, anything

	progress
		int indicating % progress

	"""
	finished = pyqtSignal()
	error = pyqtSignal(tuple)
	result = pyqtSignal(object)
	progress = pyqtSignal(int)


class RequestHandler(BaseHTTPRequestHandler):

	def do_GET(self):
		server.show_progress(self.requestline, None, 1500)
		if self.path == '/':
			path = os.path.join(os.path.dirname(__file__), 'interface.html')
			self.send_response(200)
			self.send_header('Content-Type', 'text/html');
			self.send_stat_headers(path)
			with open(path) as fh:
				self.wfile.write(fh.read().encode())
		elif self.path == '/favicon.ico':
			path = os.path.join(os.path.dirname(__file__), 'favicon.ico')
			self.send_response(200)
			self.send_header('Content-Type', 'image/vnd.microsoft.icon');
			self.send_stat_headers(path)
			with open(path, mode='rb') as fh:
				self.wfile.write(fh.read())
		else:
			self.send_response(204)	# No Content

	def send_stat_headers(self, path):
		stat = os.stat(path)
		self.send_header('Content-Length', stat.st_size)
		self.send_header('Last-Modified', self.date_time_string(stat.st_mtime))
		self.end_headers()


	def do_POST(self):
		content_length = int(self.headers['Content-Length'])
		body = self.rfile.read(content_length)
		server.show_progress(self.requestline, body.decode(), 1500)
		self.send_response(200)
		self.send_header('Content-Type', 'text/plain');
		self.end_headers()


class Server(QRunnable):

	def __init__(self):
		super(Server, self).__init__()
		self.signals = WorkerSignals()

	@pyqtSlot()
	def run(self):
		try:
			self._enabled = True
			self._http = HTTPServer(('', 8585), RequestHandler)
			self.show_progress('Listening ...', None, 0)
			self._http.serve_forever()
			self.show_progress('Closing', None, 0)
		except:
			self.err(sys.exc_info(), traceback.format_exc())
		finally:
			self.signals.finished.emit()


	def err(self, ex, tb):
		exctype, value = ex[:2]
		self.signals.error.emit((exctype, value, tb))


	def show_progress(self, stat, msg, dur):
		self.signals.result.emit({'stat': stat, 'msg': msg, 'dur': dur})


	def quit(self):
		self._http.shutdown()



class Window(QMainWindow, Ui_MainWindow):

	def __init__(self):
		global server
		super(Window, self).__init__(None)
		settings = QSettings('Voice-It', 'voice-it')
		if settings.contains('geometry'):
			self.restoreGeometry(settings.value('geometry'));
		if settings.contains('windowstate'):
			self.restoreState(settings.value('windowstate'));
		self.setupUi(self)
		self.setWindowTitle('Voice-it')
		self.copyButton.clicked.connect(self.copy)
		pixmap = QPixmap(os.path.join(os.path.dirname(__file__), 'voice-it.png'))
		self.iconLabel.setPixmap(pixmap)
		sock = socket(AF_INET, SOCK_DGRAM)
		sock.connect(('8.8.8.8', 7))
		url = ('http://%s:8585' % sock.getsockname()[0])
		self.linkLabel.setText('<a href="%s">link</a>' % url);
		self.threadpool = QThreadPool()
		server = Server()
		server.signals.result.connect(self.show_status)
		server.signals.finished.connect(self.finished)
		server.signals.error.connect(self.server_error)
		self.threadpool.start(server)

	def copy(self):
		text = self.textBox.toPlainText()
		if len(text):
			QGuiApplication.clipboard().setText(text)
			self.statusbar.showMessage('Text copied to the clipboard', 2000)

	def closeEvent(self, event):
		server.quit()
		settings = QSettings('Voice-It', 'voice-it')
		settings.setValue('geometry', self.saveGeometry())
		settings.setValue('windowstate', self.saveState())

	def show_status(self, obj):
		self.statusbar.showMessage(obj['stat'], obj['dur']);
		if obj['msg'] is not None:
			self.textBox.setPlainText(obj['msg'])

	def server_error(self, err):
		print(err)
		self.statusbar.showMessage(err[1]);

	def finished(self):
		pass


if __name__ == '__main__':
	app = QApplication(sys.argv)
	window = Window()
	window.show()
	sys.exit(app.exec())

