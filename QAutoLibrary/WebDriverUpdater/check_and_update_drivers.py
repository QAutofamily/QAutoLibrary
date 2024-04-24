from pathlib import Path
from sys import platform as _platform
from lxml import html
import platform
import argparse
import requests
import subprocess
import os
import zipfile
import tarfile
import shutil

# Allows parameters to be entered via the command line
# argparse arguments
parser = argparse.ArgumentParser()
# Path argument
parser.add_argument('--path', type=str, help='Path to webdrivers dir. Usage example Linux: WebDriverUpdater "--path /home/user/webdrivers" Windows: WebDriverUpdater "--path C:\webdrivers"')
# Browser argumenet
parser.add_argument('--browser', type=str, help='Which browser to update? Example "--browser firefox" options: chrome, firefox, edge, opera')
args = parser.parse_args()

class BrowserDriverControl():

    def __init__(self):
        self.driver_path = ""
        self.driver_file_name = ""
        self.driver_full_version = ""
        self.driver_major_version = ""
        self.browser_full_version = ""
        self.browser_major_version = ""
        self.platform = ""
        self.platform_version = ""
        self.platform_bit = ""

    def check_operating_system(self):
        self.platform = platform.system()
        self.platform_version = platform.release()
        self.platform_bit = platform.machine()

        if self.platform_bit == "AMD64" or "x86_64":
            self.platform_bit = "64"
        else:
            self.platform_bit = "32"

        self.print_os_information()

    def print_os_information(self):
        print("Operating system: " + self.platform)
        print("Version: " + self.platform_version)
        print(self.platform_bit + "-bit")

    def choose_driver_based_on_browser(self, path=None, browser=None,):
        if browser == None:
            self.check_chromeDriver(path)
        elif browser == "chrome" or browser == "Chrome" or browser == "CHROME" or browser == "gc":
            self.check_chromeDriver(path)
        elif browser == "firefox" or browser == "Firefox" or browser == "FIREFOX" or browser == "ff":
            self.check_geckoDriver(path)
        elif browser == "edge" or browser == "Edge" or browser == "EDGE" or browser == "me":
            self.check_edgeDriver(path)
        elif browser == "opera" or browser == "Opera" or browser == "OPERA" or browser == "op":
            self.check_operaDriver(path)
        elif browser == "all" or browser == "All" or browser == "ALL":
            self.check_chromeDriver()
            self.check_geckoDriver()
            self.check_edgeDriver()
            self.check_operaDriver()
        else:
            print('Browser "' + str(browser) + '" not recognized.')

    # Subprocess output usually contains additional text, these function are used to "trim" extras off
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

    def print_information(self, browser, webdriver):
        print("\n" + "Browser and webdriver information below:")
        print("- " + webdriver + " path: " + self.driver_path)
        print("- " + webdriver + " version: " + self.driver_full_version)
        print("- " + webdriver + " major version: " + self.driver_major_version)
        print("- " + browser + " version: " + self.browser_full_version)
        print("- " + browser + " major version: " + self.browser_major_version + "\n")

    def check_latest_chromeDriver_release(self):
        link = "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_" + self.browser_major_version
        f = requests.get(link)
        latest_chromeDriver_version = f.text
        return latest_chromeDriver_version

    def download_chromeDriver(self):
        # Check latest release
        if "linux" in _platform or "darwin" in _platform:
            latest_ChromeDriver_release = self.check_latest_chromeDriver_release()
            link = "https://chromedriver.storage.googleapis.com/" + latest_ChromeDriver_release + "/chromedriver_linux64.zip"
        else:
            latest_ChromeDriver_release = self.check_latest_chromeDriver_release()
            link = "https://chromedriver.storage.googleapis.com/" + latest_ChromeDriver_release + "/chromedriver_win32.zip"

        # Download latest version
        if "linux" in _platform or "darwin" in _platform:
            with open(self.driver_path + os.sep + "chromedriver_linux64.zip", "wb") as file:
                r = requests.get(link)
                file.write(r.content)
        else:
            with open(self.driver_path + os.sep + "chromedriver_win32.zip", "wb") as file:
                r = requests.get(link)
                file.write(r.content)

        # Rename old file
        if "linux" in _platform or "darwin" in _platform:
            try:
                os.rename(os.path.join(self.driver_path, "chromedriver"),
                          os.path.join(self.driver_path,
                                       "chromedriver_" + self.driver_full_version + "_old"))
                os.chmod(os.path.join(self.driver_path, "chromedriver"), 0o755)
            except Exception as e:
                print('Renaming old "chromedriver" file failed.')
                print(str(e))
        else:
            try:
                old_file = os.path.join(self.driver_path, "chromedriver.exe")
                new_file = os.path.join(self.driver_path,
                                        "OLD_" + self.driver_full_version + "_chromedriver.exe")
                os.rename(old_file, new_file)
            except Exception as e:
                print('Renaming old "chromedriver.exe" file failed.')
                print(str(e))

        # Extract zip
        if "linux" in _platform or "darwin" in _platform:
            with zipfile.ZipFile(self.driver_path + os.sep + "chromedriver_linux64.zip", 'r') as zip_ref:
                zip_ref.extractall(self.driver_path)
        else:
            with zipfile.ZipFile(self.driver_path + os.sep + "chromedriver_win32.zip", 'r') as zip_ref:
                zip_ref.extractall(self.driver_path)

        print("Latest ChromeDriver version downloaded successfully.")
        print("New installed version: " + latest_ChromeDriver_release)

    # Chrome ChromeDriver
    def check_chromeDriver(self, path=None):
        if not path == None:
            if os.path.isdir(os.path.join(path)):
                os.environ["PATH"] += os.pathsep + os.path.join(path)
                self.driver_path = path
            else:
                raise ValueError("Error, given path not found. Path: " + path)

        # Chrome versio
        if "linux" in _platform or "darwin" in _platform:
            try:
                p = subprocess.check_output(["google-chrome", " --product-version"], shell=False).decode("utf-8")
                self.browser_full_version = str(p)
                self.browser_major_version = self.get_major_version(str(p))
            except Exception as e:
                ValueError("Error! Could not get chrome version.")
                print(str(e))
        else:
            try:
                p = subprocess.Popen(r'reg.exe query "HKEY_CURRENT_USER\Software\Google\Chrome\BLBeacon" /v "version"', stdout=subprocess.PIPE, shell=False)
                output, err = p.communicate()
                p_status = p.wait()
                self.browser_full_version = output.decode("utf-8").split("REG_SZ")[-1].strip()
                self.browser_major_version = self.get_major_version(self.browser_full_version)
            except Exception as e:
                ValueError("Error! Could not get chrome version.")
                print(str(e))

        # ChromeDriver version and location
        if "linux" in _platform or "darwin" in _platform:
            try:
                p = subprocess.check_output(['which', 'chromedriver'], shell=False).decode("utf-8")
                p = p.replace("chromedriver", "")
                p = p.replace("\n", "")
                p = p.replace("\r", "")
                self.driver_path = p

                file = self.driver_path + os.sep + 'chromedriver'
                subprocess.run(['chmod', '755', file])

                p = subprocess.check_output(['chromedriver', ' --version'], shell=False).decode("utf-8")
                self.driver_major_version = self.get_major_version(str(p))
                self.driver_full_version = self.get_full_version(str(p))

            except Exception as e:
                if not path == None:
                    print("Could not get ChromeDriver version or path to driver.")
                else:
                    raise ValueError("Error! Could not get ChromeDriver version or path to driver.")
                    print(str(e))
        else:
            try:
                p = subprocess.check_output('where chromedriver', shell=False).decode("utf-8")
                p = p.replace("chromedriver.exe", "")
                p = p.replace("\r", "")
                p = p.replace("\n", "")
                self.driver_path = p

                p = subprocess.check_output('chromedriver.exe --version', shell=False).decode("utf-8")
                self.driver_major_version = self.get_major_version(str(p))
                self.driver_full_version = self.get_full_version(str(p))

            except Exception as e:
                if not path == None:
                    print("Could not get ChromeDriver version or path to driver.")
                else:
                    raise ValueError("Error! Could not get ChromeDriver version or path to driver.")
                    print(str(e))

        # Print information
        self.print_information("Chrome", "ChromeDriver" )

        if self.browser_major_version == self.driver_major_version:
            print("Chrome and ChromeDriver match. Checking latest release...")
            if (self.driver_full_version == self.check_latest_chromeDriver_release()):
                print("The current version is the latest.")
            else:
                print("New release found, trying update current version...")
                self.download_chromeDriver()

        else:
            print("Chrome and ChromeDriver does not match. Trying downloading latest release...")
            try:
                self.download_chromeDriver()
            except Exception as e:
                print("Error. Try manually updating Chrome or ChromeDriver.")
                print(str(e))

    def check_latest_geckoDriver_release(self):
        l = requests.get("https://github.com/mozilla/geckodriver/releases/latest")
        latest_geckodriver_version = str(l.url).rsplit('tag/', 1)[1]
        return latest_geckodriver_version

    def download_geckoDriver(self):
        latest_release = self.check_latest_geckoDriver_release()

        if "linux" in _platform or "darwin" in _platform:
            file_name = "geckodriver-" + latest_release + "linux64.tar.gz"
            download_link = "https://github.com/mozilla/geckodriver/releases/download/" + latest_release + "/geckodriver-" + latest_release + "-linux64.tar.gz"
            # https://github.com/mozilla/geckodriver/releases/download/v0.26.0/geckodriver-v0.26.0-linux64.tar.gz
        else:
            file_name = "geckodriver-" + latest_release + "win64.zip"
            download_link = "https://github.com/mozilla/geckodriver/releases/download/" + latest_release + "/geckodriver-" + latest_release + "-win64.zip"
            # https://github.com/mozilla/geckodriver/releases/download/v0.26.0/geckodriver-v0.26.0-win64.zip


        with open(self.driver_path + os.sep + file_name, "wb") as file:
            r = requests.get(download_link)
            file.write(r.content)

        if "linux" in _platform or "darwin" in _platform:
            try:
                os.rename(os.path.join(self.driver_path, "geckodriver"), os.path.join(self.driver_path, "geckodriver_" + self.driver_full_version + "_old"))
                os.chmod(os.path.join(self.driver_path, "geckodriver"), 0o755)
            except Exception as e:
                print('Renaming old "chromedriver" file failed.')
                print(str(e))
        else:
            try:
                old_file = os.path.join(self.driver_path, "geckodriver.exe")
                new_file = os.path.join(self.driver_path,
                                        "OLD_" + self.driver_full_version + "_geckodriver.exe")
                os.rename(old_file, new_file)
            except Exception as e:
                print('Renaming old "chromedriver.exe" file failed.')
                print(str(e))

        if "linux" in _platform or "darwin" in _platform:
            with tarfile.open(self.driver_path + os.sep + file_name, "r:gz") as tar_ref:
                def is_within_directory(directory, target):
                    
                    abs_directory = os.path.abspath(directory)
                    abs_target = os.path.abspath(target)
                
                    prefix = os.path.commonprefix([abs_directory, abs_target])
                    
                    return prefix == abs_directory
                
                def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
                
                    for member in tar.getmembers():
                        member_path = os.path.join(path, member.name)
                        if not is_within_directory(path, member_path):
                            raise Exception("Attempted Path Traversal in Tar File")
                
                    tar.extractall(path, members, numeric_owner=numeric_owner) 
                    
                
                safe_extract(tar_ref, self.driver_path)
        else:
            with zipfile.ZipFile(self.driver_path + os.sep + file_name, 'r') as zip_ref:
                zip_ref.extractall(self.driver_path)

        print("Latest GeckoDriver release downloaded successfully.")
        print("New installed version: " + latest_release)

    # Mozilla Firefox
    def check_geckoDriver(self, path=None):
        # Firefox versio
        if not path == None:
            if os.path.isdir(os.path.join(path)):
                os.environ["PATH"] += os.pathsep + os.path.join(path)
                self.driver_path = path
            else:
                raise ValueError("Error, given path not found. Path: " + path)
        try:
            if "linux" in _platform or "darwin" in _platform:
                p = subprocess.check_output(['firefox', '--version'], shell=False).decode("utf-8")
            else:
                p = subprocess.check_output('firefox -v | more', shell=False).decode("utf-8")

            self.browser_major_version = self.get_major_version(str(p))
            self.browser_full_version = self.get_full_version(str(p))

        except Exception as e:
            raise ValueError("Error! Could not get firefox version.")
            print(str(e))

        #GeckoDriver version and location
        try:
            if "linux" in _platform or "darwin" in _platform:
                file = self.driver_path + os.sep + 'geckodriver'
                subprocess.run(['chmod', '755', file])
                p = subprocess.check_output(['geckodriver', '--version'], shell=False).decode("utf-8")
            else:
                p = subprocess.check_output('geckodriver --version', shell=False).decode("utf-8")

            self.driver_full_version = self.get_full_version(str(p))
            self.driver_full_version = "v" + self.driver_full_version

            if "linux" in _platform or "darwin" in _platform:
                p = subprocess.check_output(['which', 'geckodriver'], shell=False).decode("utf-8")
                p = p.replace("\n", "")
                p = p.replace("\r", "")
                p = p.replace("geckodriver", "")
            else:
                p = subprocess.check_output(('where geckodriver'), shell=False).decode("utf-8")
                p = p.replace("\n", "")
                p = p.replace("\r", "")
                p = p.replace("geckodriver.exe", "")

            self.driver_path = str(p)

        except Exception as e:
            if not path == None:
                print("Could not get GeckoDriver version or path.")
            else:
                raise ValueError("Error! Could not get GeckoDriver version or path.")
                print(str(e))

        self.print_information("Firefox", "GeckoDriver")

        if int(self.browser_major_version) > 60:
            if (self.check_latest_geckoDriver_release() == self.driver_full_version):
                print("GeckoDriver is up to date")
            else:
                print("Trying to download latest release...")
                self.download_geckoDriver()
        else:
            print("Firefox version too old, update firefox manually.")

    # Downloads text file which include latest version, depending on major numbers.
    def check_latest_edgeDriver_release(self):
        # List of webdriver versions https://msedgewebdriverstorage.z22.web.core.windows.net/
        latest_release_link = "https://msedgedriver.azureedge.net/LATEST_RELEASE_" + self.browser_major_version
        file_name = "LATEST_RELEASE_" + self.browser_major_version

        # Download text file which includes newest version
        with open(self.driver_path + os.sep + file_name, "wb") as file:
            r = requests.get(latest_release_link)
            file.write(r.content)

        # Read file using errors='ignore' and encoding.
        with open(self.driver_path + os.sep + file_name, "r", errors='ignore', encoding='utf-8') as file:
            latest_release = file.read()

        # Fix the readed text.
        latest_release_fix = ""
        for char in latest_release:
            if char.isdigit() or char == ".":
                latest_release_fix += char

        return latest_release_fix

    def download_webDriver(self):
        latest_release = self.check_latest_edgeDriver_release()

        download_link = "https://msedgedriver.azureedge.net/" + latest_release + "/edgedriver_win64.zip"
         # https://msedgedriver.azureedge.net/86.0.585.0/edgedriver_win64.zip

        with open(self.driver_path + os.sep + "edgedriver_win64.zip", "wb") as file:
            r = requests.get(download_link)
            file.write(r.content)

        try:
            old_file = os.path.join(self.driver_path, "msedgedriver.exe")
            new_file = os.path.join(self.driver_path, "OLD_" + self.driver_full_version + "_msedgedriver.exe")
            os.rename(old_file, new_file)
        except Exception as e:
            print('Renaming old "msedgedriver.exe" file failed.')
            print(str(e))

        with zipfile.ZipFile(self.driver_path + os.sep + "edgedriver_win64.zip", 'r') as zip_ref:
                zip_ref.extractall(self.driver_path)

        print("Latest WebDriver downloaded successfully.")
        print("New installed version: " + latest_release)

    # Microsoft Edge
    # Linux version is coming in year 2021
    def check_edgeDriver(self, path=None):
        if not path == None:
            if os.path.isdir(os.path.join(path)):
                os.environ["PATH"] += os.pathsep + os.path.join(path)
                self.driver_path = path
            else:
                raise ValueError("Error, given path not found. Path: " + path)

        # Microsoft Edge version
        try:
            p = subprocess.check_output('reg.exe QUERY "HKEY_CURRENT_USER\Software\Microsoft\Edge\BLBeacon" /t REG_SZ /reg:32 /v version', shell=False).decode("utf-8")
            self.browser_major_version = self.get_major_version(str(p))
            self.browser_full_version = self.get_full_version(str(p))

        except Exception as e:
            raise ValueError("Error! Could not get edge version.")
            print(str(e))

        # Edge driver
        try:
            p = subprocess.check_output('msedgedriver --version', shell=False).decode("utf-8")
            self.driver_major_version = self.get_major_version(str(p))
            self.driver_full_version = self.get_full_version(str(p))

            p = subprocess.check_output('where msedgedriver', shell=False).decode("utf-8")
            p = p.replace("msedgedriver.exe", "")
            p = p.replace("\n", "")
            p = p.replace("\r", "")
            self.driver_path = str(p)

        except Exception as e:
            if not path == None:
                print("Could not get edge version or path to driver.")
            else:
                raise ValueError("Error! Could not get edge webdriver version or path to driver.")
                print(str(e))

        self.print_information("Microsoft Edge", "WebDriver")

        if self.browser_major_version == self.driver_major_version:
            print("Edge and WebDriver match. Checking latest release...")
            if self.driver_full_version != self.check_latest_edgeDriver_release():
                print("New release found, trying update current version...")
                self.download_webDriver()
            else:
                print("Current WebDriver version is latest.")

        else:
            print("Edge and WebDriver does not match. Trying downloading new version.")
            self.download_webDriver()

    # https://github.com/operasoftware/operachromiumdriver/releases/latest
    def check_latest_operaDriver_release(self):
        page = requests.get("https://github.com/operasoftware/operachromiumdriver/releases/latest")
        latest_release = str(page.url).rsplit('tag/', 1)[1]

        # Use xpath to get text which include supported Opera version and take last two characters
        tree = html.fromstring(page.content)
        content = tree.xpath('//a[contains(text(),"Opera Stable")]')
        supported_opera_version = str(content[0].text)[-2:]
        return latest_release, supported_opera_version

    def download_operaDriver(self):
        latest_release, supported_opera_version  = self.check_latest_operaDriver_release()

        if not supported_opera_version == self.browser_major_version:
            print("Current Opera version does not support latest OperaDriver release. Update Opera manually to " + supported_opera_version + " version.")
            return

        if "linux" in _platform or "darwin" in _platform:
            download_link = "https://github.com/operasoftware/operachromiumdriver/releases/download/" + latest_release + "/operadriver_linux64.zip"
            file_name = "operadriver_linux64.zip"
        else:
            download_link = "https://github.com/operasoftware/operachromiumdriver/releases/download/" + latest_release + "/operadriver_win64.zip"
            file_name = "operadriver_win64.zip"


        with open(self.driver_path + os.sep + file_name, "wb") as file:
            r = requests.get(download_link)
            file.write(r.content)

        if "linux" in _platform or "darwin" in _platform:
            try:
                os.rename(os.path.join(self.driver_path, "operadriver"),
                          os.path.join(self.driver_path, "operadriver_" + self.driver_full_version + "_old"))
            except Exception as e:
                print('Renaming old "operadriver" file failed.')
                print(str(e))
        else:
            try:
                old_file = os.path.join(self.driver_path, "operadriver.exe")
                new_file = os.path.join(self.driver_path, "OLD_" + self.driver_full_version + "_operadriver.exe")
                os.rename(old_file, new_file)
            except Exception as e:
                print('Renaming old "operadriver.exe" file failed.')
                print(str(e))


        with zipfile.ZipFile(self.driver_path + os.sep + file_name, 'r') as zip_ref:
            zip_ref.extractall(self.driver_path)

        # Move files
        if "linux" in _platform or "darwin" in _platform:
            try:
                shutil.move(self.driver_path + os.sep + "operadriver_linux64" + os.sep + "operadriver",
                            self.driver_path + os.sep + "operadriver")
                shutil.move(self.driver_path + os.sep + "operadriver_linux64" + os.sep + "sha512_sum",
                            self.driver_path + os.sep + "sha512_sum")

                # If folder is empty, delete
                if len(os.listdir(self.driver_path + os.sep + "operadriver_linux64")) == 0:
                    shutil.rmtree(self.driver_path + os.sep + "operadriver_linux64")

                os.chmod(self.driver_path + os.sep + "operadriver", 0o755)
                os.chmod(self.driver_path + os.sep + "sha512_sum", 0o755)

            except Exception as e:
                raise OSError("Fail to move files.")
        else:
            try:
                shutil.move(self.driver_path + os.sep + "operadriver_win64" + os.sep + "operadriver.exe",
                            self.driver_path + os.sep + "operadriver.exe")
                shutil.move(self.driver_path + os.sep + "operadriver_win64" + os.sep + "sha512_sum",
                            self.driver_path + os.sep + "sha512_sum")

                if len(os.listdir(self.driver_path + os.sep + "operadriver_win64")) == 0:
                    shutil.rmtree(self.driver_path + os.sep + "operadriver_win64")
            except Exception as e:
                raise OSError("Fail to move files.")

        print("Latest OperaDriver release downloaded successfully.")
        print("New installed version: " + latest_release)

    # Opera version
    def check_operaDriver(self, path=None):
        if not path == None:
            if os.path.isdir(os.path.join(path)):
                os.environ["PATH"] += os.pathsep + os.path.join(path)
                self.driver_path = path
            else:
                raise ValueError("Error, given path not found. Path: " + path)

        # Notice that if you give normal cmd command "opera --version" -> doesn't print anything, but this subprocess.check_output does.
        try:
            if "linux" in _platform or "darwin" in _platform:
                p = subprocess.check_output(['opera', '--version'], shell=False).decode("utf-8")
            else:
                p = subprocess.check_output(['launcher', '--version'], shell=False).decode("utf-8")

            self.browser_major_version = self.get_major_version(str(p))
            self.browser_full_version = self.get_full_version(str(p))

        except Exception as e:
            raise ValueError("Error! Could not get opera version.")
            print(str(e))

        #OperaDriver version and location
        try:
            if "linux" in _platform or "darwin" in _platform:
                file = self.driver_path + os.sep + 'operadriver'
                subprocess.run(['chmod', '755', file])
                p = subprocess.check_output(['operadriver', '--version'], shell=False).decode("utf-8")
            else:
                p = subprocess.check_output('operadriver --version', shell=False).decode("utf-8")

            self.driver_full_version = "v." + self.get_full_version(str(p))
            self.driver_major_version = self.get_major_version(str(p))

            if "linux" in _platform or "darwin" in _platform:
                p = subprocess.check_output(['which', 'operadriver'], shell=False).decode("utf-8")
                p = p.replace("\n", "")
                p = p.replace("\r", "")
                p = p[:-11]
            else:
                p = subprocess.check_output(('where operadriver'), shell=False).decode("utf-8")
                p = p.replace("\n", "")
                p = p.replace("\r", "")
                p = p.replace("operadriver.exe", "")

            self.driver_path = str(p)

        except Exception as e:
            if not path == None:
                print("OperaDriver not found.")
            else:
                raise ValueError("Error! Could not get OperaDriver version or path.")
                print(str(e))

        self.print_information("Opera", "OperaDriver")

        if self.browser_major_version < "69":
            print("Opera version too old, update Opera browser manually.")
        elif self.browser_major_version == "69" and self.driver_major_version == "83":
            print("Current Opera browser and OperaDriver match.")
        elif self.browser_major_version == "70" and self.driver_major_version == "84":
            print("Current Opera browser and OperaDriver match.")
        else:
            print("Current Opera browser and OperaDriver does not match. Checking latest release...")
            self.download_operaDriver()

if __name__ == '__main__':
    driverpath = os.path.join(Path.home(), "webdrivers")
    driver_checker = BrowserDriverControl()
    #driver_checker.check_operating_system()
    #driver_checker.choose_driver_based_on_browser(args.path, args.browser)
    driver_checker.choose_driver_based_on_browser(driverpath, args.browser)

def main():

    driverpath = os.path.join(Path.home(), "webdrivers")
    driver_checker = BrowserDriverControl()
    #driver_checker.choose_driver_based_on_browser(args.path, args.browser)
    driver_checker.choose_driver_based_on_browser(driverpath, args.browser)




