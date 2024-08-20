import fitz
import os
import re

def extract_processes(text, page_num, caderno_name):
    # Padrão para identificar o início de um processo
    process_start_pattern = r'Processo\s+\d{7,}-\d{2}\.\d{4}\.\d{1,2}\.\d{2}\.\d{4}'
    # Padrão para identificar o advogado
    adv_pattern = r'ADV:\s+(.+?)(?=\s+-|$)'

    lines = text.split('\n')
    processes = []
    current_process = []
    capturing = False
    include_process = False

    for line in lines:
        if re.search(process_start_pattern, line):  # Verifica se a linha é o início de um processo
            if capturing:  # Se já estava capturando um processo, finaliza e começa um novo
                if include_process:
                    process_text = " ".join(current_process)
                    adv_match = re.search(adv_pattern, process_text)
                    adv_name = adv_match.group(1).strip() if adv_match else "Não identificado"
                    processes.append((process_text, page_num, caderno_name, adv_name))
                current_process = []  # Reinicia para o próximo processo
                include_process = False  # Reinicia o filtro de inclusão
            capturing = True
        
        if capturing:
            current_process.append(line.strip())
            # Verifica se o processo atual deve ser incluído
            if "nomeação de perito".lower() in line.lower():
                include_process = True

    # Adiciona o último processo capturado se atender ao critério
    if capturing and include_process:
        process_text = " ".join(current_process)
        adv_match = re.search(adv_pattern, process_text)
        adv_name = adv_match.group(1).strip() if adv_match else "Não identificado"
        processes.append((process_text, page_num, caderno_name, adv_name))

    return processes

def process_pdf(file_path, output_dir):
    doc = fitz.open(file_path)
    file_name = os.path.basename(file_path).replace('.pdf', '')
    output_file = os.path.join(output_dir, f"{file_name}_results.txt")

    with open(output_file, 'w', encoding='utf-8') as f:
        for page_num in range(doc.page_count):
            page = doc.load_page(page_num)
            text = page.get_text("text")  # Extrai o texto no formato bruto
            results = extract_processes(text, page_num + 1, file_name)
            
            for process_text, page_number, caderno, adv_name in results:
                f.write(f"Caderno: {caderno}\n")
                f.write(f"Página: {page_number}\n\n")
                f.write(f"{process_text}\n\n")
                f.write(f"Advogado: {adv_name}\n")
                f.write("\n" + "="*50 + "\n\n")

def process_all_pdfs(pdf_directory, output_directory):
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    
    for file_name in os.listdir(pdf_directory):
        if file_name.endswith(".pdf"):
            file_path = os.path.join(pdf_directory, file_name)
            process_pdf(file_path, output_directory)
            
# Diretórios de entrada e saída
pdf_directory = "C:\\Users\\mathe\\Desktop\\input"  # Pasta onde estão os PDFs
output_directory = "C:\\Users\\mathe\\Desktop\\output"  # Pasta onde serão salvos os resultados

# Executa o processamento
process_all_pdfs(pdf_directory, output_directory)
