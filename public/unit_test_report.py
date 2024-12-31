
# -*- coding: utf-8 -*-

'''
You can using this py script to realize your custom html reporter:
    - pip install Mako
    - ./template/unit_test_template.html
    - ./unit_test_log/...
'''

import os
from mako.template import Template
from mako.runtime import Context
from io import StringIO


class UnitTestLogReporter():
    def __init__(self, dir=None):
        self.path = dir
        self.log_lines = []
        self.file_list = []
        self.render_parameter_list = {"title": "MCAL Test", "global_result": True, "test_engineer": "Zhu", "test_version": "1.0", "test_config": "Unknown" }
        self.render_parameter_list["modules"] = ""
        self.hardware_info = {"paltform":"Unknown", "driver_version": "0.0.0", "framework_version": "1.0"}
        if dir is not None:
            files = os.listdir(dir)
            for file in files:
                if file.find("unit_test") != -1:
                    file_info = file.split(" ")
                    if len(file_info) == 3:
                        self.file_list.append(file)
    
    def setDir(self, dir=None):
        if dir is not None:
            self.path = dir
            files = os.listdir(dir)
            for file in files:
                if file.find("unit_test") != -1:
                    file_info = file.split(" ")
                    if len(file_info) == 3:
                        self.file_list.append(file)
    
    def addHardwareInfo(self, paltform="stm32g431rbt6", driver_version="0.0.0", framework_version="1.0"):
        self.hardware_info = {"paltform":paltform, "driver_version": driver_version, "framework_version": framework_version}

    def setTestTitle(self, title):
        self.render_parameter_list["title"] = title

    def setTestEngineer(self, name):
        self.render_parameter_list["test_engineer"] = name

    def setTestVersion(self, version):
        self.render_parameter_list["test_version"] = version

    def setTestModule(self, module):
        self.render_parameter_list["modules"] = module

    def runReporter(self):
        test_cases = []
        num_of_all_case = 0
        num_of_pass_case = 0
        test_log_detail = []
        test_case_detail = {}
        test_case_step_detail = []

        self.file_list.sort()
    
        self.render_parameter_list["global_begin_time"] = self.file_list[0][10:23] + ":" + self.file_list[0][23:25] + ":" + self.file_list[0][25:27]
        self.render_parameter_list["global_end_time"] = self.file_list[-1][10:23] + ":" + self.file_list[-1][23:25] + ":" + self.file_list[-1][25:27]
        
        for item in self.file_list:
            with open(self.path + "/" + item,'r', encoding='UTF-8') as f:
                self.log_lines = f.readlines()

            file_info = item.split(" ")
            test_time = file_info[1] + " " + file_info[2][0:2] + ":" + file_info[2][2:4] + ":" + file_info[2][4:6]

            for line in self.log_lines:
                line_items = line.split(':')
                if line_items[0].find("UNIT") != -1:
                    line_infos = line_items[1].split('|')
                    # delete "\n"
                    line_infos[-1] = line_infos[-1][:-1] 
                    if len(line_infos) == 5:
                        test_case_step_detail.append({"index": line_infos[0], "time_stamp": line_infos[1], "api": line_infos[2], "description": line_infos[3], "result": line_infos[4]})
                        if line_infos[4].find("fail") != -1:
                            test_case_detail["result"] = False
                    else:
                        if line_infos[0].find("END") != -1:
                            test_case_detail["steps"] = test_case_step_detail
                            test_case_detail["begin_time_stamp"] = test_case_step_detail[0]["time_stamp"]
                            test_case_detail["end_time_stamp"] = test_case_step_detail[-1]["time_stamp"]
                            test_cases.append(test_case_detail)
                        if line_infos[0].find("BEGIN") != -1:
                            num_of_all_case += 1
                            test_case_detail = {"index": num_of_all_case, "title": line_infos[1], "description": line_infos[1], "result": True, "begin_time": test_time, "end_time": test_time}
                            test_case_step_detail = []

            test_log_detail.append({"begin_time":"0.0", "end_time":test_cases[-1]["steps"][-1]["time_stamp"], "file_path": self.path + "/" + item})

        for item in test_cases:
            if item["result"] is True:
                num_of_pass_case += 1
            else:
                self.render_parameter_list["global_result"] = False

        self.render_parameter_list["num_of_all_test_case"] = num_of_all_case
        self.render_parameter_list["num_of_exec_test_case"] = num_of_all_case
        self.render_parameter_list["num_of_pass_test_case"] = num_of_pass_case

        self.render_parameter_list["test_cases_info"] = test_cases
        self.render_parameter_list["test_log_info"] = test_log_detail
        self.render_parameter_list["hardware_infomation"] = self.hardware_info

        mytemplate = Template(filename='./template/unit_test_template.html')
        buf = StringIO()
        ctx = Context(buf, **self.render_parameter_list)
        mytemplate.render_context(ctx)

        with open("./unit_test_log/report.html",'w', encoding='UTF-8', newline="") as f:
            f.write(buf.getvalue())


if __name__ == "__main__":
    current_directory = os.path.dirname(os.path.abspath(__file__))
    reporter = UnitTestLogReporter(current_directory + "/unit_test_log")
    reporter.setTestModule("spi_flash,fatfs(ff)")
    reporter.runReporter()














