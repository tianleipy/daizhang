import os
import unittest
import time
import HTMLTestRunner
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

cur_path = os.path.dirname(os.path.realpath(__file__))


def add_case(casename="case", rule="test*.py"):
    """加载全部测试用例"""
    case_path = os.path.join(cur_path, casename)
    if not os.path.exists(case_path):
        os.mkdir(case_path)
    print("测试用例路径：%s" % case_path)
    discover = unittest.defaultTestLoader.discover(case_path, pattern=rule, top_level_dir=None)
    print(discover)
    return discover


def run_case(all_case, reportname="report"):
    """执行全部测试用例，并生成测试报告"""
    now = time.strftime("%Y.%m.%d.%H.%M.%S")
    report_path = os.path.join(cur_path, reportname)
    if not os.path.exists(report_path):
        os.mkdir(report_path)
    report_abspath = os.path.join(report_path, now+"result.html")
    with open(report_abspath, 'wb') as f:
        runner = HTMLTestRunner.HTMLTestRunner(stream=f, title="自动化测试报告，结果如下：", description="用例执行情况：")
        runner.run(all_case)


def get_refile(report_path):
    """获取最新的测试报告，如果生成的测试报告不加时间戳这步可注释"""
    lists = os.listdir(report_path)
    lists.sort(key=lambda fn: os.path.getmtime(os.path.join(report_path, fn)))
    print(lists)
    report_file = os.path.join(report_path, lists[-1])
    return report_file


def sendmail(sender, psw, receiver, smtpserver, report_file, port):
    with open(report_file, 'rb') as f:
        mail_body = f.read()
    msg = MIMEMultipart()
    body = MIMEText(mail_body, _subtype='html', _charset='utf-8')
    msg['Subject'] = "自动化测试报告"
    msg['from'] = sender
    msg['to'] = psw
    msg.attach(body)
    # 添加附件
    att = MIMEText(open(report_file, 'rb').read(), "base64", "utf-8")
    att["Content-Type"] = "application/octet-stream"
    att["Content-Disposition"] = 'attachment; filename = "report.html"'
    msg.attach(att)
    try:
        smtp = smtplib.SMTP_SSL(smtpserver, port)
    except:
        smtp = smtplib.SMTP()
        smtp.connect(smtpserver, port)
    # 登录发送
    smtp.login(sender, psw)
    smtp.sendmail(sender, receiver, msg.as_string())
    smtp.quit()
    print("测试报告邮件已发送！")


if __name__ == '__main__':
    all_case = add_case()
    run_case(all_case)
    report_path = os.path.join(cur_path, "report")
    report_file = get_refile(report_path)
    from config import readconfig
    sender = readconfig.sender
    port = readconfig.port
    psw = readconfig.psw
    smtp_server = readconfig.smtp_server
    receiver = readconfig.receiver
    sendmail(sender, psw, receiver, smtp_server, report_file, port)
