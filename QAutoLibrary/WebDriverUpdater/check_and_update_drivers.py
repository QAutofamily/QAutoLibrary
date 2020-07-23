from sys import platform as _platform
import argparse
import webbrowser
import requests
import subprocess
import os
import sys
import urllib
import zipfile

# argparse argumenttien antamiseen komentoriviltä
parser = argparse.ArgumentParser()

# Vaihtoehto polku
parser.add_argument('--path', type=str, help='Path to webdrive dir.')

# Vaihtoehto polku
parser.add_argument('--browser', type=str, help='Which browser to update?.')

args = parser.parse_args()

# En tiedä toimiiko tälleen suoraan.
# if not args.browser == "":
#     self.chromeDriver_path = args.browser

class BrowserDriverControl():

    def __init__(self):
        self.chromeDriver_path = ""
        self.chromeDriver_full_version = ""
        self.chromeDriver_major_version = ""
        self.chrome_full_version = ""
        self.chrome_major_version = ""
        # Linux
        # /home/jenkins/webdrivers
        # Windows
        # QAutoRPA\\webdrivers

    def get_major_version(self, string):
        for numbers in string.split():
            # print(numbers)

            if "." in numbers:
                major_version = str(numbers.split(".")[0])
                return major_version
                break

    def get_full_version(self, string):
        for numbers in string.split():
            if "." in numbers:
                complete_version = str(numbers)
                return complete_version
                break

    def print_information(self):
        print("Tiedot alla.")
        print("ChromeDriver polku: " + self.chromeDriver_path)
        print("ChromeDriver versio: " + self.chromeDriver_full_version)
        print("ChromeDriver versio suurin: " + self.chromeDriver_major_version)
        print("Chrome versio: " + self.chrome_full_version)
        print("Chrome versio suurin: " + self.chrome_major_version)

    def check_latest_chromeDriver_release(self):
        link = "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_" + self.chrome_major_version
        f = requests.get(link)
        latest_chromeDriver_version = f.text
        print("Uusin versio: " + latest_chromeDriver_version)
        return latest_chromeDriver_version

    def download_ChromeDriver(self):
        # Nimeä vanha tiedosto uusiksi
        if "linux" in _platform or "darwin" in _platform:
            try:
                os.rename(os.path.join(self.chromeDriver_path, "chromedriver"),
                          os.path.join(self.chromeDriver_path,
                                       "chromedriver_" + self.chromeDriver_full_version + "_old"))
                os.chmod(os.path.join(self.chromeDriver_path, "chromedriver"), 0o755)
            except Exception as e:
                print('Renaming old "chromedriver" file failed.')
                print(str(e))
        else:
            try:
                old_file = os.path.join(self.chromeDriver_path, "chromedriver.exe")
                new_file = os.path.join(self.chromeDriver_path,
                                        "OLD_" + self.chromeDriver_full_version + "_chromedriver.exe")
                os.rename(old_file, new_file)
            except Exception as e:
                print('Renaming old "chromedriver.exe" file failed.')
                print(str(e))

        # Tarkista uusin versio
        if "linux" in _platform or "darwin" in _platform:
            latest_ChromeDriver_release = self.check_latest_chromeDriver_release()
            link = "https://chromedriver.storage.googleapis.com/" + latest_ChromeDriver_release + "/chromedriver_linux64.zip"
        else:
            latest_ChromeDriver_release = self.check_latest_chromeDriver_release()
            link = "https://chromedriver.storage.googleapis.com/" + latest_ChromeDriver_release + "/chromedriver_win32.zip"

        # Ladataan uusin versio
        if "linux" in _platform or "darwin" in _platform:
            with open(self.chromeDriver_path + os.sep + "chromedriver_linux64.zip", "wb") as file:
                r = requests.get(link)
                file.write(r.content)
        else:
            with open(self.chromeDriver_path + os.sep + "chromedriver_win32.zip", "wb") as file:
                r = requests.get(link)
                file.write(r.content)

        # Puretaan zippi
        if "linux" in _platform or "darwin" in _platform:
            with zipfile.ZipFile(self.chromeDriver_path + os.sep + "chromedriver_linux64.zip",
                                 'r') as zip_ref:
                # Puretaan tiedosto webdrivers hakemiston alle.
                zip_ref.extractall(self.chromeDriver_path)
        else:
            with zipfile.ZipFile(self.chromeDriver_path + os.sep + "chromedriver_win32.zip",
                                 'r') as zip_ref:
                # Puretaan tiedosto webdrivers hakemiston alle.
                zip_ref.extractall(self.chromeDriver_path)

        print("Latest ChromeDriver version downloaded successfully. New version: " + latest_ChromeDriver_release)

    def check_chromeDriver_and_chrome(self, path=None):
        if path == None:
            if "linux" in _platform or "darwin" in _platform:
                try:
                    p = subprocess.check_output(['which', 'chromedriver'], shell=False).decode("utf-8")
                    p = p.replace("chromedriver", "")
                    self.chromeDriver_path = p.strip()
                    print("ChromeDriver path found: " + self.chromeDriver_path)
                except Exception as e:
                    raise ValueError("Error! ChromeDriver path not found.")
                    print(str(e))
            else:
                try:
                    p = subprocess.check_output('where chromedriver', shell=False).decode("utf-8")
                    p = p.replace("chromedriver.exe", "")
                    self.chromeDriver_path = p.strip()
                    print("ChromeDriver path found: " + self.chromeDriver_path)
                except Exception as e:
                    raise ValueError("Error! ChromeDriver path not found.")
                    print(str(e))

        else:
            print("Annettu polku: " + str(path))
            if os.path.isdir(os.path.join(path)):
                os.environ["PATH"] += os.pathsep + os.path.join(path)
                self.chromeDriver_path = path
            else:
                raise ValueError("Error, given path not found. Path: " + path)

        if "linux" in _platform or "darwin" in _platform:
            try:
                # Antaa chromedriver tiedostolle 755 oikeudet
                file = self.chromeDriver_path + os.sep + 'chromedriver'
                subprocess.run(['chmod', '755', file])
                p = subprocess.check_output(['chromedriver', ' --version'], shell=False).decode("utf-8")
                self.chromeDriver_major_version = self.get_major_version(str(p))
                self.chromeDriver_full_version = self.get_full_version(str(p))
            except Exception as e:
                print("Error! Could not get ChromeDriver version.")
                print(str(e))

        else:
            try:
                p = subprocess.check_output('chromedriver.exe --version', shell=False).decode("utf-8")
                self.chromeDriver_major_version = self.get_major_version(str(p))
                self.chromeDriver_full_version = self.get_full_version(str(p))
            except Exception as e:
                print("Error! Could not get ChromeDriver version.")
                print(str(e))

        # Chrome versio
        if "linux" in _platform or "darwin" in _platform:
            try:
                p = subprocess.check_output(["google-chrome", " --product-version"], shell=False).decode("utf-8")
                self.chrome_full_version = str(p)
                self.chrome_major_version = self.get_major_version(str(p))
            except Exception as e:
                print("Error! Could not get chrome version.")
                print(str(e))

        else:
            try:
                p = subprocess.Popen(
                    r'reg.exe query "HKEY_CURRENT_USER\Software\Google\Chrome\BLBeacon" /v "version"',
                    stdout=subprocess.PIPE, shell=False)
                output, err = p.communicate()
                p_status = p.wait()
                self.chrome_full_version = output.decode("utf-8").split("REG_SZ")[-1].strip()
                self.chrome_major_version = self.get_major_version(self.chrome_full_version)
            except Exception as e:
                print("Error! Could not get chrome version.")
                print(str(e))

        # Tähän tietojen tulostus
        self.print_information()

        if self.chrome_major_version == self.chromeDriver_major_version:
            print("Chrome and ChromeDriver match. Checking latest release...")
            if (self.chromeDriver_full_version == self.check_latest_chromeDriver_release()):
                print("The current version is the latest.")
            else:
                print("New release found, trying update current version...")
                self.download_ChromeDriver()

        else:
            print("Chrome and ChromeDriver does not match. Trying downloading latest release...")
            try:
                self.download_ChromeDriver()
            except Exception as e:
                print("Error. Try manually updating Chrome or ChromeDriver.")
                print(str(e))

if __name__ == '__main__':
    driver_checker = BrowserDriverControl()
    driver_checker.check_chromeDriver_and_chrome(args.path)

def main():
    driver_checker = BrowserDriverControl()
    driver_checker.check_chromeDriver_and_chrome(args.path)




