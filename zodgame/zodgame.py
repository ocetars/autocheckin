# encoding=utf8
import io
import re
import sys
import time

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import undetected_chromedriver as uc
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By

def zodgame_checkin(driver, formhash):
    checkin_url = "https://zodgame.xyz/plugin.php?id=dsu_paulsign:sign&operation=qiandao&infloat=1&inajax=0"    
    checkin_query = """
        (function (){
        var request = new XMLHttpRequest();
        var fd = new FormData();
        fd.append("formhash","%s");
        fd.append("qdxq","kx");
        request.open("POST","%s",false);
        request.withCredentials=true;
        request.send(fd);
        return request;
        })();
        """ % (formhash, checkin_url)
    checkin_query = checkin_query.replace("\n", "")
    driver.set_script_timeout(240)
    resp = driver.execute_script("return " + checkin_query)
    match = re.search('<div class="c">\r\n(.*?)</div>\r\n', resp["response"], re.S)
    message = match[1] if match is not None else "签到失败"
    print(f"【签到】{message}")
    return "恭喜你签到成功!" in message or "您今日已经签到，请明天再来" in message


def zodgame_task(driver, formhash):

    def clear_handles(driver, main_handle):
        handles = driver.window_handles[:]
        for handle in handles:
            if handle != main_handle:
                driver.switch_to.window(handle)
                driver.close()
        driver.switch_to.window(main_handle)
      
    def show_task_reward(driver):
        driver.get("https://zodgame.xyz/plugin.php?id=jnbux")
        try:
            WebDriverWait(driver, 240).until(
                lambda x: x.title != "Just a moment..."
            )
            reward = driver.find_element(By.XPATH, '//li[contains(text(), "点币: ")]').get_attribute("textContent")[:-2]
            print(f"【Log】{reward}")
        except:
            pass

    driver.get("https://zodgame.xyz/plugin.php?id=jnbux")
    WebDriverWait(driver, 240).until(
        lambda x: x.title != "Just a moment..."
    )

    join_bux = driver.find_elements(By.XPATH, '//font[text()="开始参与任务"]')
    if len(join_bux) != 0 :    
        driver.get(f"https://zodgame.xyz/plugin.php?id=jnbux:jnbux&do=join&formhash={formhash}")
        WebDriverWait(driver, 240).until(
            lambda x: x.title != "Just a moment..."
        )
        driver.get("https://zodgame.xyz/plugin.php?id=jnbux")
        WebDriverWait(driver, 240).until(
            lambda x: x.title != "Just a moment..."
        )

    join_task_a = driver.find_elements(By.XPATH, '//a[text()="参与任务"]')
    success = True

    if len(join_task_a) == 0:
        print("【任务】所有任务均已完成。")
        return success
    handle = driver.current_window_handle
    for idx, a in enumerate(join_task_a):
        on_click = a.get_attribute("onclick")
        try:
            function = re.search("""openNewWindow(.*?)\(\)""", on_click, re.S)[0]
            script = driver.find_element(By.XPATH, f'//script[contains(text(), "{function}")]').get_attribute("text")
            task_url = re.search("""window.open\("(.*)", "newwindow"\)""", script, re.S)[1]
            driver.execute_script(f"""window.open("https://zodgame.xyz/{task_url}")""")
            driver.switch_to.window(driver.window_handles[-1])
            try:
                WebDriverWait(driver, 240).until(
                    lambda x: x.find_elements(By.XPATH, '//div[text()="成功！"]')
                )
            except:
                print(f"【Log】任务 {idx+1} 广告页检查失败。")
                pass

            try:    
                check_url = re.search("""showWindow\('check', '(.*)'\);""", on_click, re.S)[1]
                driver.get(f"https://zodgame.xyz/{check_url}")
                WebDriverWait(driver, 240).until(
                    lambda x: len(x.find_elements(By.XPATH, '//p[contains(text(), "检查成功, 积分已经加入您的帐户中")]')) != 0 
                        or x.title == "BUX广告点击赚积分 - ZodGame论坛 - Powered by Discuz!"
                )
            except:
                print(f"【Log】任务 {idx+1} 确认页检查失败。")
                pass

            print(f"【任务】任务 {idx+1} 成功。")
        except Exception as e:
            success = False
            print(f"【任务】任务 {idx+1} 失败。", type(e))
        finally:
            clear_handles(driver, handle)
    
    show_task_reward(driver)

    return success

def zodgame(cookie_string):
    max_retries = 5
    
    for attempt in range(1, max_retries + 1):
        driver = None
        try:
            print(f"\n【系统】开始第 {attempt} 次执行任务...")
            options = uc.ChromeOptions()
            options.add_argument("--disable-popup-blocking")
            
            # 使用 raw string (r) 避免 Python 转义字符报错
            driver = uc.Chrome(driver_executable_path = r"C:\SeleniumWebDrivers\ChromeDriver\chromedriver.exe",
                               browser_executable_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                               options = options)

            # Load cookie
            driver.get("https://zodgame.xyz/")

            if cookie_string.startswith("cookie:"):
                cookie_string = cookie_string[len("cookie:"):]
            cookie_string = cookie_string.replace("/","%2")
            
            # 增加对空字符的安全过滤 if '=' in x
            cookie_dict = [ 
                {"name" : x.split('=')[0].strip(), "value": x.split('=')[1].strip()} 
                for x in cookie_string.split(';') if '=' in x
            ]

            driver.delete_all_cookies()
            for cookie in cookie_dict:
                if cookie["name"] in ["qhMq_2132_saltkey", "qhMq_2132_auth"]:
                    driver.add_cookie({
                        "domain": "zodgame.xyz",
                        "name": cookie["name"],
                        "value": cookie["value"],
                        "path": "/",
                    })
            
            driver.get("https://zodgame.xyz/")
            
            WebDriverWait(driver, 240).until(
                lambda x: x.title != "Just a moment..."
            )
            assert len(driver.find_elements(By.XPATH, '//a[text()="用户名"]')) == 0, "Login fails. Please check your cookie."
                
            formhash = driver.find_element(By.XPATH, '//input[@name="formhash"]').get_attribute('value')
            assert zodgame_checkin(driver, formhash) and zodgame_task(driver, formhash), "Checkin failed or task failed."

            print(f"【系统】恭喜！所有流程在第 {attempt} 次尝试时圆满成功！")
            return  # 成功后直接退出函数

        except Exception as e:
            print(f"【系统】第 {attempt} 次执行失败，错误信息: {e}")
            if attempt < max_retries:
                print(f"【系统】等待 30 秒后进行第 {attempt + 1} 次重试...\n")
                time.sleep(30)
            else:
                print("【系统】已达到最大失败次数 (5次)，整体任务失败。")
                sys.exit(1) # 超过 5 次则抛出错误并退出脚本
                
        finally:
            # 确保不论成功或失败，都把当前的 driver 关闭，防止后台残留残留 Chrome 进程卡死电脑
            if driver:
                try:
                    driver.close()
                    driver.quit()
                except:
                    pass
    
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("【错误】未传入 Cookie 参数。")
        sys.exit(1)
        
    cookie_string = sys.argv[1]
    assert cookie_string
    
    zodgame(cookie_string)
