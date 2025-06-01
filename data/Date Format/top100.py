import requests
import datetime
from dateutil.relativedelta import relativedelta
import html

# Read the input file
filename = "testCase/inputs/AllPrevious_Day_Publish_events.csv"
with open(filename, 'r', encoding='utf-8') as fp:
    lines = fp.read().splitlines()

html_output = ["<html><body><table border='1' width='100%'>",
               "<thead><td>Id</td><td>Website</td><td>Start</td><td>End</td><td>Status</td></thead>"]

timeout = 30  # seconds
headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/70.0.3538.77 Chrome/70.0.3538.77 Safari/537.36',
           'Accept': '*/*'}

for line in lines:
    if not line.strip():
        continue
    id_fields = line.split('\t')
    if len(id_fields) < 5:
        continue
    id_val = id_fields[0]
    url = id_fields[2]
    start_date = id_fields[3]
    end_date = id_fields[4]
    csv_data = ""
    try:
        resp = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True, verify=False)
        Wval = resp.text
    except Exception as e:
        Wval = ""
    # Date parsing
    try:
        st_dt_obj = datetime.datetime.strptime(start_date, '%Y-%m-%d')
        en_dt_obj = datetime.datetime.strptime(end_date, '%Y-%m-%d')
    except Exception:
        html_output.append(f"<tr><td>{id_val}</td><td><a href='{html.escape(url)}'>{html.escape(url)}</a></td><td>{html.escape(start_date)}</td><td>{html.escape(end_date)}</td><td>Invalid date</td></tr>")
        continue
    st_dt = st_dt_obj.day
    en_dt = en_dt_obj.day
    st_dt0 = st_dt_obj.strftime('%d')
    en_dt0 = en_dt_obj.strftime('%d')
    st_OrdDt = st_dt_obj.strftime('%-d') + st_dt_obj.strftime('%-d') if hasattr(st_dt_obj, 'strftime') else str(st_dt)  # fallback
    en_OrdDt = en_dt_obj.strftime('%-d') + en_dt_obj.strftime('%-d') if hasattr(en_dt_obj, 'strftime') else str(en_dt)
    st_mn = st_dt_obj.month
    en_mn = en_dt_obj.month
    st_mn0 = st_dt_obj.strftime('%m')
    en_mn0 = en_dt_obj.strftime('%m')
    st_mn_s = st_dt_obj.strftime('%b')
    en_mn_s = en_dt_obj.strftime('%b')
    st_mn_f = st_dt_obj.strftime('%B')
    en_mn_f = en_dt_obj.strftime('%B')
    st_day_s = st_dt_obj.strftime('%a')
    en_day_s = en_dt_obj.strftime('%a')
    st_day_f = st_dt_obj.strftime('%A')
    en_day_f = en_dt_obj.strftime('%A')
    st_yr = st_dt_obj.strftime('%Y')
    en_yr = en_dt_obj.strftime('%Y')
    st_yr2 = st_dt_obj.strftime('%y')
    en_yr2 = en_dt_obj.strftime('%y')
    # Only a few formats for brevity, add more as needed
    format_list = [
        f"{st_day_f}, {st_mn_f} {st_dt}, {st_yr}",
        f"{st_mn_f} {st_dt}, {st_yr}",
        f"{st_dt} {st_mn_s} - {en_dt} {en_mn_s} {en_yr}",
        f"{st_mn_s}. {st_dt} - {en_dt}, {en_yr}" if st_mn == en_mn else "",
        f"{st_mn_s} {st_dt}, {st_yr} - {en_mn_s} {en_dt}, {en_yr}",
        f"{st_mn_f} {st_dt}-{en_dt}, {en_yr}" if st_mn == en_mn else "",
        f"{st_mn_f} {st_dt} - {en_dt}, {en_yr}" if st_mn == en_mn else "",
        f"{st_dt}-{en_dt} {en_mn_f}'{en_yr2}" if st_mn == en_mn else "",
        f"{st_dt0}.{st_mn0}.{st_yr}-{en_dt0}.{en_mn0}.{en_yr}",
        f"{st_day_f}, {st_mn_f} {st_dt}, {st_yr}",
        f"{st_day_f}, {st_mn_f} {st_dt}, {st_yr} to {en_day_f}, {en_mn_f} {en_dt}, {en_yr}",
        f"{st_day_f}, {st_mn_f} {st_dt}, {st_yr}",
        f"{st_day_f}, {st_mn_f} {st_dt}, {st_yr}",
        f"{st_day_f}, {st_mn_f} {st_dt}, {st_yr}",
        f"{st_day_f}, {st_mn_f} {st_dt}, {st_yr}",
    ]
    dateFound = False
    for fmt in format_list:
        if fmt and fmt in Wval:
            csv_data = fmt
            dateFound = True
            break
    html_output.append(f"<tr><td>{id_val}</td><td><a href='{html.escape(url)}'>{html.escape(url)}</a></td><td>{html.escape(start_date)}</td><td>{html.escape(end_date)}</td><td>{html.escape(csv_data)}</td></tr>")

html_output.append("</table></body></html>")

with open("testCase/outputs/top100_output.html", "w", encoding="utf-8") as f:
    f.write("\n".join(html_output))

print("Done. Output written to top100_output.html")
