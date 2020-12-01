import json
import os
from pprint import pp, pprint
# from jsonschema import validate


TYPES = {
        'string': str,
        'integer': int,
        'object': dict,
        'array': list,
        'null': type(None),
        'boolean': bool,
        'number': [int, float]
    }


def get_type(types, val):
    for key, value in types.items():
        if value == val:
            return key


def json_validate(instance, schema, json_file_name):

    errors = {}
    errors_and_solution = []
    
    require_properties = schema.get('required')
    property_data = instance.get('data')
    properties = schema.get('properties')
    

    if property_data is None:
        errors_and_solution.append(('В json файле отсутсвуют данные', 'Добавьте необходимые данные в свойство data'))
    else:
        for property in require_properties:
            if property not in instance.keys() and property not in property_data.keys():
                errors_and_solution.append((f'Отсутсвует обязательное свойство {property}.', 'Добавьте \
                    его, или убедитесь в правильности написания.'))
    

        unset_properties = []

        for property in property_data:
            
            if property not in properties:
                unset_properties.append(property)
            else:
                property_type_schema = properties[property].get('type')
                property_type_json = type(property_data[property])

                if isinstance(property_type_schema, list):
                    schema_types_to_python_type = [TYPES[i] for i in property_type_schema]
                    
                    if property_type_json not in schema_types_to_python_type:
                        errors_and_solution.append((f'Свойству {property} присвоено значение неверного \
                            типа ({get_type(TYPES, property_type_json)})', f'Присвойте свойству значение одного из следующих типов: {property_type_schema}'))
                   
                else:
                    if property_type_json is not TYPES.get(property_type_schema):
                        errors_and_solution.append((f'Свойству {property} присвоено значение неверного \
                            типа ({get_type(TYPES, property_type_json)})', f'Присвойте свойству значение типа {property_type_schema}'))

        if unset_properties:
            errors_and_solution.append((f'В json присутсвуют не заданные свойства: {", ".join(unset_properties)}', 'Удалите не заданные свойства'))


        for property in properties:
            if properties[property].get('type') == 'array':
                if type(property_data.get(property)) is list:
                    errors_and_solution += validate_inner_property(property, property_data.get(property), properties[property])


    errors['name'] = json_file_name
    errors['errors'] = []
    errors['solution'] = []

    for error in errors_and_solution:  
        errors['errors'].append(error[0])
        errors['solution'].append(error[1])    


    return errors


def validate_inner_property(property_name, inner_property, inner_schema):

    inner_errors_and_solution = []

    inner_require_properties = inner_schema['items']['required']

    for i, p in enumerate(inner_property, start=1):

        if type(inner_schema['items']['type']) is list:
            inner_types_to_python_type = [TYPES[i] for i in inner_schema['items']['type']]
        
            if type(p) not in inner_types_to_python_type:
                inner_errors_and_solution.append((f'Элементу свойства {property_name} присвоено значение неверного \
                    типа ({get_type(TYPES, type(p))})', f'Присвойте элементу значение одного из следующих типов: {inner_schema["items"]["type"]}'))
                   
        else:
            if type(p) is not TYPES.get(inner_schema['items']['type']):
                inner_errors_and_solution.append((f'Элементу свойства {property_name} присвоено значение неверного \
                    типа ({get_type(TYPES, type(p))})', f'Присвойте элементу значение типа {inner_schema["items"]["type"]}'))

    
        for property in inner_require_properties:
            if property not in p.keys():
                inner_errors_and_solution.append((f'У {i}-го элемента свойства {property_name} отсутсвует обязательное свойство {property}.', 'Добавьте \
                    его, или убедитесь в правильности написания.'))
            

    return inner_errors_and_solution


def generate_html(data):

    html = """<html><table border="3">
    <tr><th>File name</th><th>Errors</th><th>Solution</th><th>Is validate?</th></tr>"""

    for file in data:
        html += f"<tr><td>{file['name']}</td>"

        errors = ""
        solutions = ""

        for i, val in enumerate(zip(file['errors'], file['solution']), start=1):
            errors += f"{i}. {val[0]} </br>"
            solutions += f"{i}. {val[1]} </br>"            

        html += f"<td>{errors}</td>"
        html += f"<td>{solutions}</td>"
        
        is_validate = 'Нет' if file['errors'] else 'Да'
        
        html += f"<td>{is_validate}</td>"
        html += "</tr>"
    
    html += "</table></html>"

    with open('result.html', 'w', encoding='utf-8') as f:
        f.write(html)
        

def main():

    total_errors = []

    json_files_path = 'unziped_files/task_folder/event'
    schema_files_path = 'unziped_files/task_folder/schema'

    json_files = os.listdir(json_files_path)
    schema_files = os.listdir(schema_files_path)


    for file in json_files:
        with open(f'{json_files_path}/{file}', 'r', encoding='utf-8') as f:
            loaded_json = json.load(f)
            
            if loaded_json is not None and loaded_json:
                event = loaded_json.get('event')
                
                if f'{event}.schema' not in schema_files:
                    total_errors.append({
                        'name': file,
                        'errors': ['Схема не найдена.'], 
                        'solution': ['Создайте необходимую схему.']})
                else:
                    schema = json.loads(open(f'{schema_files_path}/{event}.schema').read())
                    total_errors.append(json_validate(instance=loaded_json, schema=schema, json_file_name=file))

            else:
                total_errors.append({
                    'name': file, 
                    'errors': ['Json файл пустой.'], 
                    'solution': ['Заполните json данными.']})

  
    # pprint(total_errors, sort_dicts=False) 
    generate_html(total_errors)


if __name__ == '__main__':
    main()
       