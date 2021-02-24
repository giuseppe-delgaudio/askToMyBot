import re


async def replace(template: dict, data:dict):
        
        str_temp = str(template)
        for key in data:
            pattern = "\${"+key+"}"
            str_temp = re.sub(pattern, str(data[key]),str_temp)        
        return eval(str_temp)
