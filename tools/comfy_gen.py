"""Generate the Tornado card picture with the local ComfyUI (Krea-2 turbo), headless.

    py tools/comfy_gen.py <out.png> [seed ...]
ComfyUI must run on 127.0.0.1:8188 (python_embeded ... main.py --listen 127.0.0.1).
"""
import json
import sys
import time
import urllib.request

HOST = 'http://127.0.0.1:8188'
PROMPT = ('Dark fantasy spell card painting: a tall swirling tornado of pale blue-white wind and '
          'crackling lightning, funnel narrow at the bottom touching the ground and wide at the top, '
          'debris and small rocks circling it, pitch black night background, soft glow around the '
          'vortex, painterly 2000s PC RPG game art, centered, high contrast, no text, no frame, no border')


def graph(seed, w, h):
    return {
        '10': {'class_type': 'UNETLoader', 'inputs': {'unet_name': 'krea2_turbo_fp8_scaled.safetensors', 'weight_dtype': 'default'}},
        '11': {'class_type': 'CLIPLoader', 'inputs': {'clip_name': 'qwen3vl_4b_fp8_scaled.safetensors', 'type': 'krea2', 'device': 'default'}},
        '12': {'class_type': 'VAELoader', 'inputs': {'vae_name': 'qwen_image_vae.safetensors'}},
        '6': {'class_type': 'CLIPTextEncode', 'inputs': {'text': PROMPT, 'clip': ['11', 0]}},
        '13': {'class_type': 'ConditioningZeroOut', 'inputs': {'conditioning': ['6', 0]}},
        '5': {'class_type': 'EmptyLatentImage', 'inputs': {'width': w, 'height': h, 'batch_size': 1}},
        '3': {'class_type': 'KSampler', 'inputs': {'seed': seed, 'steps': 8, 'cfg': 1.0, 'sampler_name': 'euler',
                                                   'scheduler': 'simple', 'denoise': 1.0, 'model': ['10', 0],
                                                   'positive': ['6', 0], 'negative': ['13', 0], 'latent_image': ['5', 0]}},
        '8': {'class_type': 'VAEDecode', 'inputs': {'samples': ['3', 0], 'vae': ['12', 0]}},
        '9': {'class_type': 'SaveImage', 'inputs': {'images': ['8', 0], 'filename_prefix': 'SpellRework_tornado'}},
    }


def run(seed, out):
    body = json.dumps({'prompt': graph(seed, 768, 1024)}).encode()
    r = json.load(urllib.request.urlopen(urllib.request.Request(HOST + '/prompt', body, {'Content-Type': 'application/json'})))
    pid = r['prompt_id']
    for _ in range(600):
        time.sleep(2)
        h = json.load(urllib.request.urlopen(HOST + '/history/' + pid))
        if pid in h:
            st = h[pid].get('status', {})
            if st.get('status_str') == 'error':
                raise SystemExit(json.dumps(st)[:2000])
            for node in h[pid]['outputs'].values():
                for img in node.get('images', []):
                    q = 'filename=%s&subfolder=%s&type=%s' % (img['filename'], img['subfolder'], img['type'])
                    open(out, 'wb').write(urllib.request.urlopen(HOST + '/view?' + q).read())
                    print('wrote', out)
                    return
    raise SystemExit('timeout')


if __name__ == '__main__':
    out = sys.argv[1]
    seeds = [int(s) for s in sys.argv[2:]] or [1]
    for s in seeds:
        run(s, out.replace('.png', '_%d.png' % s) if len(seeds) > 1 else out)
