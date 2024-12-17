import os
import sys
import argparse
import re
import threading
import math
import shutil
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib import parse

def exec_unary_math_oper(oper, val):
    result = float('nan')
    if oper=="log":
        result = math.log10(val)
    elif oper=="ln":
        result = math.log(val)
    elif oper=="lg":
        result = math.log2(val)
    elif oper=="sin":
        result = math.sin(math.radians(val))
    elif oper=="cos":
        result = math.cos(math.radians(val))
    elif oper=="sec":
        result = 1/math.cos(math.radians(val))
    elif oper=="tan":
        result = math.tan(math.radians(val))
    elif oper=="fat":
        result = math.factorial(int(val))
    elif oper=="sq":
        result = val * val
    elif oper=="sqrt":
        result = math.sqrt(val)
    elif oper=="abs":
        if val < 0:
            val=-val
        result = val
    elif oper=="inv":
        result = 1/val
    return result

def exec_binary_math_oper(oper, val1,val2):
    result = float('nan')
    if oper=="add":
        result = val1 + val2
    elif oper=="sub":
        result = val1 - val2
    elif oper=="mul":
        result = val1 * val2
    elif oper=="div" and val2!=0.0:
        result = val1 / val2
    elif oper=="pow":
        result = math.pow(val1,val2)
    return result

ServerDir = "."
ServerDefaultFile = "index.html"

class ServidorWebBasico(BaseHTTPRequestHandler):
    def do_GET(self):
        if re.search("/wscalc/", self.path):
            print("wscalc")
            query = parse.parse_qs(parse.urlparse(self.path).query)

            op = query.get("op", [""])[0]
            val1 = query.get("n1", [""])[0]
            val2 = query.get("n2", [""])[0]

            print(val1)
            print(val2)
            print(op)

            if not (op and val1 and val2):
                self.send_error(400, "Parâmetros inválidos. Verifique os números e operadores na requisição.")
                return
            try:
                if val1 != "und":
                    val1 = float(val1)
                if val2 != "und":
                    val2 = float(val2)
            except ValueError:
                self.send_error(400, "Os valores val1 e val2 devem ser números.")
                return
            if val2 == "und":
                result = exec_unary_math_oper(oper=op, val=val1)
            elif val1 == "und":
                result = exec_unary_math_oper(oper=op, val=val2)
            else:
                result = exec_binary_math_oper(oper=op, val1=val1, val2=val2)
            result = round(result, 6)
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(f"{result}".encode("utf-8"))     
            return
        else:
            print("self.path=",self.path)
            if ServerDir[0]=='.':
                filepath = os.getcwd()
                if len(ServerDir)>2:                 
                    filepath = os.path.join(filepath,ServerDir[2:])
            else:
                filepath = ServerDir
            if self.path=="/":
                filepath = os.path.join(filepath,ServerDefaultFile)
            else:
                words = self.path.split('/')
                for word in words:
                    filepath = os.path.join(filepath, word)
            if os.path.isdir(filepath):
                self.send_error(403, "Forbidden")
                return
            try:
                f = open(filepath, 'rb')
            except IOError:
                self.send_error(404, "File not found")
                return 
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            fs = os.fstat(f.fileno())
            self.send_header("Content-Length", str(fs[6]))
            self.send_header("Last-Modified", self.date_time_string(fs.st_mtime))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            shutil.copyfileobj(f, self.wfile)
            f.close()
        return

def main():
    global ServerDir, ServerDefaulFile
    parser = argparse.ArgumentParser(description="Servidor Web Basico")
    parser.add_argument("start")
    parser.add_argument("-port", type=int, default=8080, help="Porta do servidor")
    parser.add_argument("-ip", default="0.0.0.0", help="Endereco IP do servidor")
    parser.add_argument("-dir", default="./pages", help="Diretorio base do servidor")
    parser.add_argument("-file", default="index.html", help="Pagina default do servidor")
    args = parser.parse_args()
    
    ServerDir = args.dir
    ServerDefaultFile = args.file
    
    server = HTTPServer((args.ip, args.port), ServidorWebBasico)
    
    print("Servidor WSCalc iniciado.")
    print("Parametros do servidor:")
    print("    IP:                 ", args.ip)
    print("    Porta:              ", args.port)
    print("    Diretorio Corrente: ", os.getcwd())
    print("    HomePage Dir:       ", args.dir)
    print("    HomePage File:      ", args.file)
    print("Pressione CTRL-C para parar o servidor.")
    
    server.serve_forever()


if __name__ == "__main__":
    main()