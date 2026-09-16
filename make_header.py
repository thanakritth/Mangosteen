import gzip
import os

html_path = r'c:\AlahiMangosteen\index.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# Update settings paths
html = html.replace("cameraSettingsIframe.src = settingsUrl;", "cameraSettingsIframe.src = '/settings';")
html = html.replace("openNewTabLink.href = settingsUrl;", "openNewTabLink.href = '/settings';")

gz_data = gzip.compress(html.encode('utf-8'), compresslevel=9)
out_path = r'c:\AlahiMangosteen\LilyGo-Camera-Series-master\LilyGo-Camera-Series-master\examples\t_sim_cam_factory\mangosteen_html.h'

with open(out_path, 'w', encoding='utf-8') as out:
    out.write('#ifndef __MANGOSTEEN_HTML_H__\n#define __MANGOSTEEN_HTML_H__\n\n')
    out.write(f'#define mangosteen_html_gz_len {len(gz_data)}\n')
    out.write('const uint8_t mangosteen_html_gz[] = {\n')
    for i in range(0, len(gz_data), 16):
        chunk = gz_data[i:i+16]
        hex_chunk = ', '.join(f'0x{b:02X}' for b in chunk)
        out.write(f'    {hex_chunk},\n')
    out.write('};\n\n#endif // __MANGOSTEEN_HTML_H__\n')

print(f'Generated mangosteen_html.h successfully, size: {len(gz_data)} bytes')
