import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime

PRODUCTS = {
    "Soja": "https://cepea.org.br/br/indicador/soja.aspx",
    "Café": "https://cepea.org.br/br/indicador/cafe.aspx",
    "Açúcar": "https://cepea.org.br/br/indicador/acucar.aspx",
    "Boi": "https://cepea.org.br/br/indicador/boi-gordo.aspx",
    "Milho": "https://cepea.org.br/br/indicador/milho.aspx",
    "Trigo": "https://cepea.org.br/br/indicador/trigo.aspx",
    "Etanol": "https://cepea.org.br/br/indicador/etanol.aspx",
    "Frango": "https://cepea.org.br/br/indicador/frango.aspx",
    "Suíno": "https://cepea.org.br/br/indicador/suino.aspx",
    "Ovos": "https://cepea.org.br/br/indicador/ovos.aspx",
    "Leite": "https://cepea.org.br/br/indicador/leite.aspx",
    "Citrus": "https://cepea.org.br/br/indicador/citros.aspx"
}

def scrape_cepea_news(headers):
    url = "https://cepea.org.br/br"
    news_data = []
    print("Iniciando captura de extras (Releases/Opinião)...")
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # RELEASES - Localizado em .imagenet-box2
            releases_section = soup.find('div', class_='imagenet-box2')
            if releases_section:
                for a in releases_section.find_all('a', href=True):
                    # Ignora links de "ver mais"
                    if 'ver mais' in a.get_text().lower(): continue
                    title = a.get_text(strip=True)
                    if title and len(title) > 10:
                        link = a['href']
                        if not link.startswith('http'): link = "https://cepea.org.br" + link
                        news_data.append({
                            "title": title.replace('RELEASES', '').strip(),
                            "link": link,
                            "category_label": "AGRO",
                            "timestamp": int(datetime.now().timestamp() * 1000)
                        })

            # OPINIÃO CEPEA - Localizado em .imagenet-box4
            opiniao_section = soup.find('div', class_='imagenet-box4')
            if opiniao_section:
                for item in opiniao_section.find_all('div', class_='imagenet-bloco-article2'):
                    a = item.find('a', href=True)
                    if a:
                        # Extrai o título ignorando o nome do autor se possível
                        full_text = a.get_text(strip=True)
                        link = a['href']
                        if not link.startswith('http'): link = "https://cepea.org.br" + link
                        news_data.append({
                            "title": "OPINIÃO: " + full_text,
                            "link": link,
                            "category_label": "COMODITY",
                            "timestamp": int(datetime.now().timestamp() * 1000)
                        })
            
            # Fallback per keyword if boxes changed
            if not news_data:
                for h2 in soup.find_all('h2'):
                    if 'RELEASES' in h2.text.upper():
                        container = h2.find_parent('div')
                        if container:
                            for a in container.find_all('a', href=True):
                                if 'ver mais' in a.get_text().lower(): continue
                                title = a.get_text(strip=True)
                                if title and len(title) > 10:
                                    link = a['href']
                                    if not link.startswith('http'): link = "https://cepea.org.br" + link
                                    news_data.append({"title": title, "link": link, "category_label": "AGRO", "timestamp": int(datetime.now().timestamp()*1000)})

        print(f"Extras captured: {len(news_data)} items.")
        if news_data:
            os.makedirs('.tmp', exist_ok=True)
            with open('.tmp/cepea_news.js', 'w', encoding='utf-8') as f:
                f.write(f"window.cepeaNews = {json.dumps(news_data, ensure_ascii=False)};")
    except Exception as e:
        print(f"Erro ao extrair news do CEPEA: {e}")

def scrape_cepea():
    data = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    for name, url in PRODUCTS.items():
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                table = None
                for t in soup.find_all('table'):
                    if name == "Leite" and "litro" in t.text.lower():
                        table = t
                        break
                    if "," in t.text:
                        table = t
                        break
                
                if not table:
                    table = soup.find('table', {'class': 'imagenet-tabela'})
                
                if table:
                    rows = table.find_all('tr')
                    if len(rows) > 1:
                        if name in ["Ovos", "Suíno"]:
                            for r in rows[1:]:
                                c = r.find_all('td')
                                if len(c) >= 3:
                                    p_txt = c[2].get_text(strip=True) if len(c) > 3 else c[1].get_text(strip=True)
                                    v_txt = c[3].get_text(strip=True) if len(c) > 3 else c[2].get_text(strip=True)
                                    if not any(char.isdigit() for char in p_txt): continue
                                    data.append({"name": name, "price": p_txt, "variation": v_txt, "updated": datetime.now().strftime("%H:%M")})
                                    break
                            continue
                        
                        if name == "Leite":
                            first_price = None
                            region = None
                            found_milk = False
                            for i, r in enumerate(rows):
                                c = r.find_all('td')
                                if len(c) >= 3:
                                    p_val = c[2].get_text(strip=True).replace('.', '').replace(',', '.')
                                    try:
                                        p_float = float(p_val)
                                        if not first_price:
                                            first_price = p_float
                                            region = c[1].get_text(strip=True)
                                            continue
                                        if c[1].get_text(strip=True) == region:
                                            prev_price = p_float
                                            var = ((first_price / prev_price) - 1) * 100
                                            price = f"{first_price:.4f}".replace('.', ',')
                                            variation = f"{var:+.2f}%".replace('.', ',')
                                            data.append({"name": name, "price": price, "variation": variation, "updated": datetime.now().strftime("%H:%M")})
                                            found_milk = True
                                            break
                                    except: continue
                            if found_milk: continue
                            if first_price:
                                data.append({"name": name, "price": f"{first_price:.4f}".replace('.', ','), "variation": "0,00%", "updated": datetime.now().strftime("%H:%M")})
                            continue

                        data_row = rows[1]
                        cols = data_row.find_all('td')
                        if len(cols) >= 3:
                            price = cols[1].get_text(strip=True)
                            variation = cols[2].get_text(strip=True)
                            data.append({
                                "name": name,
                                "price": price,
                                "variation": variation,
                                "updated": datetime.now().strftime("%H:%M")
                            })
                            continue
            data.append({"name": name, "price": "N/D", "variation": "0%", "updated": "--:--"})
        except Exception as e:
            data.append({"name": name, "price": "Erro", "variation": "0%", "updated": "--:--"})

    # Captura Extras
    scrape_cepea_news(headers)

    # Salvar resultados no diretório raiz para visibilidade total (Local + Web)
    try:
        # 1. Salva o JSON principal (Para APIs, GitHub Actions e Servidores Web)
        with open('cepea_data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        
        # 2. Salva o JS para injeção de Script (Fallback para abertura local via file://)
        with open('cepea_data.js', 'w', encoding='utf-8') as f:
            f.write(f"renderCommodities({json.dumps(data, ensure_ascii=False)});")

        # Opcional: Salvar em .tmp para histórico local
        os.makedirs('.tmp', exist_ok=True)
        with open('.tmp/cepea_data_history.json', 'a', encoding='utf-8') as f:
            log_entry = {"timestamp": datetime.now().isoformat(), "data": data}
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
            
        print(f"Sucesso: {len(data)} produtos salvos em JSON e JS para compatibilidade máxima.")
    except Exception as e:
        print(f"Erro ao salvar arquivos: {e}")

if __name__ == "__main__":
    scrape_cepea()
