import time
import win32serviceutil
import win32service
import win32event
import win32api
import servicemanager
import logging

from main import processacupom  # Substitua 'your_script' pelo nome do arquivo original

class AppServerSvc(win32serviceutil.ServiceFramework):
    _svc_name_ = "GeradorNumSorte"
    _svc_display_name_ = "Serviço de geração dos números da sorte"
    _svc_description_ = "Esse é um serviço que gera números para o sistema de campanhas"
    
    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.is_running = True
        self.log("Service starting...")
        self.main()

    def SvcStop(self):
        self.log("Service is stopping...")
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        self.is_running = False
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        self.log("Service is starting...")
        # Call your main function here
        self.main()

    def main(self):
        while self.is_running:
            try:
                processacupom()  # Call your process function
                time.sleep(36000)  # Sleep for 10 hours
            except Exception as e:
                self.log(f"An error occurred: {e}")
                time.sleep(60)  # Sleep for 1 minute before retrying

    def log(self, msg):
        servicemanager.LogInfoMsg(msg)

if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(AppServerSvc)