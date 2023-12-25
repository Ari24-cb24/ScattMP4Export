import subprocess
import json
import re
import os

from converter.document_types import ScattDocument


class Converter:
    SHELL_INIT = r"C:\Windows\SysWoW64\cmd.exe /c "
    COMMA_FIX_FIND = re.compile(r"(\d+),(\d+)")
    COMMA_FIX_REPLACE = r"\1.\2"

    @classmethod
    def __execute_command(cls, filename: str):
        cdir = os.path.dirname(os.path.realpath(__file__))
        rpath = os.path.join(cdir, "../scatt2json.vbs")

        proc = subprocess.Popen(cls.SHELL_INIT + f" cscript {rpath} " + filename, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        out, err = proc.communicate()
        print("Output:", out)
        print("Errors:", err)

    @classmethod
    def __fix_json(cls, filename: str):
        with open(filename, "r") as file:
            content = file.read()

        content = cls.COMMA_FIX_FIND.sub(cls.COMMA_FIX_REPLACE, content)

        with open(filename, "w") as file:
            file.write(content)

    @classmethod
    def __parse_json(cls, filename: str) -> ScattDocument:
        with open(filename, "r") as file:
            data = json.load(file)

        return ScattDocument.from_json(data)

    @classmethod
    def convert(cls, filename: str, skip_converting: bool = False) -> ScattDocument:
        full_path = os.path.abspath(filename)
        output_location = os.path.abspath(filename.replace(".scatt", "") + ".json")

        if not skip_converting:
            cls.__execute_command(full_path)
            cls.__fix_json(output_location)

        return cls.__parse_json(output_location)

