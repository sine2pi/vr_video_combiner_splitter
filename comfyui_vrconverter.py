import os
import subprocess
import json
import glob

# Helper functions
def have(a):
    return a is not None and str(a).strip() != ""

def bitrate(input_file):
    cmd = ['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_format', '-show_streams', input_file]
    result = subprocess.run(cmd, capture_output=True, text=True)
    try:
        data = json.loads(result.stdout)
        return data.get('format', {}).get('bit_rate')
    except:
        return None

def frame_rate(file_path):
    cmd = ['ffprobe','-v', 'error','-select_streams', 'v:0','-show_entries', 'stream=width,height,duration,r_frame_rate,nb_frames','-of', 'json', file_path]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    info = json.loads(result.stdout)
    stream = info['streams'][0]
    fps_str = stream.get('r_frame_rate', '30/1')
    num, denom = map(int, fps_str.split('/'))
    fps = num / denom if denom != 0 else 30.0
    return fps

def vcodec(file_path):
    cmd = ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=codec_name", "-of", "csv=p=0", file_path]
    codec = subprocess.check_output(cmd).decode(errors='ignore').strip()
    return codec

def vresolution(file_path):
    cmd = ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of", "csv=p=0:s=x", file_path]
    res = subprocess.check_output(cmd).decode(errors='ignore').strip()
    parts = res.split('x')
    if len(parts) == 2:
        return int(parts[0]), int(parts[1])
    return 0, 0

def run_process(cmd, log_callback=None, process_callback=None):
    if log_callback:
        log_callback(f"Executing: {' '.join(cmd)}")
    else:
        print(f"Executing: {' '.join(cmd)}")
        
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, errors='replace')
    if process_callback: process_callback(process)
    
    for line in process.stdout:
        if log_callback: 
            log_callback(line.strip())
        else:
            print(line.strip())
            
    process.wait()
    if process.returncode != 0:
        raise Exception(f"Command failed with code {process.returncode}")

import json
RAW_ENCODERS_DATA = json.loads(r'''[
    {
        "id": "prores-422-proxy-win",
        "encoder": "ProRes",
        "profile": "422 Proxy",
        "allowsAlpha": 0,
        "ffmpegOpts": "-c:v prores_ks -profile:v 0 -vendor apl0 -quant_mat lt -bits_per_mb 525 -pix_fmt yuv422p10le",
        "ext": [
            "mov"
        ],
        "os": "windows|linux",
        "minSize": [
            1,
            1
        ],
        "maxSize": [
            16386,
            16386
        ],
        "maxBitDepth": 10,
        "doNotScaleFullColorRange": "transcode"
    },
    {
        "id": "prores-422-std-win",
        "encoder": "ProRes",
        "profile": "422 Std",
        "allowsAlpha": 0,
        "ffmpegOpts": "-c:v prores_ks -profile:v 2 -vendor apl0 -quant_mat hq -bits_per_mb 1350 -pix_fmt yuv422p10le",
        "ext": [
            "mov"
        ],
        "os": "windows|linux",
        "minSize": [
            1,
            1
        ],
        "maxSize": [
            16386,
            16386
        ],
        "maxBitDepth": 10,
        "doNotScaleFullColorRange": "transcode"
    },
    {
        "id": "prores-422-lt-win",
        "encoder": "ProRes",
        "profile": "422 LT",
        "allowsAlpha": 0,
        "ffmpegOpts": "-c:v prores_ks -profile:v 1 -vendor apl0 -quant_mat lt -bits_per_mb 525 -pix_fmt yuv422p10le",
        "ext": [
            "mov"
        ],
        "os": "windows|linux",
        "minSize": [
            1,
            1
        ],
        "maxSize": [
            16386,
            16386
        ],
        "maxBitDepth": 10,
        "doNotScaleFullColorRange": "transcode"
    },
    {
        "id": "prores-422-hq-win",
        "encoder": "ProRes",
        "profile": "422 HQ",
        "allowsAlpha": 0,
        "ffmpegOpts": "-c:v prores_ks -profile:v 3 -vendor apl0 -quant_mat hq -bits_per_mb 1350 -pix_fmt yuv422p10le",
        "ext": [
            "mov"
        ],
        "os": "windows|linux",
        "minSize": [
            1,
            1
        ],
        "maxSize": [
            16386,
            16386
        ],
        "maxBitDepth": 10,
        "doNotScaleFullColorRange": "transcode"
    },
    {
        "id": "dnxhr-lb",
        "encoder": "DNxHR",
        "profile": "LB",
        "allowsAlpha": 0,
        "ffmpegOpts": "-strict experimental -c:v dnxhd -profile:v dnxhr_lb -pix_fmt yuv422p",
        "ext": [
            "mov",
            "mxf"
        ],
        "os": "windows|linux",
        "minSize": [
            1,
            1
        ],
        "maxSize": [
            16386,
            16386
        ],
        "maxBitDepth": 8,
        "doNotScaleFullColorRange": "transcode"
    },
    {
        "id": "dnxhr-sq",
        "encoder": "DNxHR",
        "profile": "SQ",
        "allowsAlpha": 0,
        "ffmpegOpts": "-strict experimental -c:v dnxhd -profile:v dnxhr_sq -pix_fmt yuv422p",
        "ext": [
            "mov",
            "mxf"
        ],
        "os": "windows|linux",
        "minSize": [
            1,
            1
        ],
        "maxSize": [
            16386,
            16386
        ],
        "maxBitDepth": 8,
        "doNotScaleFullColorRange": "transcode"
    },
    {
        "id": "dnxhr-hq",
        "encoder": "DNxHR",
        "profile": "HQ",
        "allowsAlpha": 0,
        "ffmpegOpts": "-strict experimental -c:v dnxhd -profile:v dnxhr_hq -pix_fmt yuv422p",
        "ext": [
            "mov",
            "mxf"
        ],
        "os": "windows|linux",
        "minSize": [
            1,
            1
        ],
        "maxSize": [
            16386,
            16386
        ],
        "maxBitDepth": 8,
        "doNotScaleFullColorRange": "transcode"
    },
    {
        "id": "dnxhr-hqx",
        "encoder": "DNxHR",
        "profile": "HQX",
        "allowsAlpha": 0,
        "ffmpegOpts": "-strict experimental -c:v dnxhd -profile:v dnxhr_hqx -pix_fmt yuv422p10le",
        "ext": [
            "mov",
            "mxf"
        ],
        "os": "windows|linux",
        "minSize": [
            1,
            1
        ],
        "maxSize": [
            16386,
            16386
        ],
        "maxBitDepth": 12,
        "doNotScaleFullColorRange": "transcode"
    },
    {
        "id": "dnxhr-444",
        "encoder": "DNxHR",
        "profile": "444",
        "allowsAlpha": 0,
        "ffmpegOpts": "-strict experimental -c:v dnxhd -profile:v dnxhr_444 -pix_fmt yuv444p10le",
        "ext": [
            "mov",
            "mxf"
        ],
        "os": "windows|linux",
        "minSize": [
            1,
            1
        ],
        "maxSize": [
            16386,
            16386
        ],
        "maxBitDepth": 12,
        "doNotScaleFullColorRange": "transcode"
    },
    {
        "id": "h264-main-win-nvidia",
        "encoder": "H264",
        "profile": "High",
        "allowsAlpha": 0,
        "gpu": "nvidia",
        "ffmpegOpts": "-c:v h264_nvenc -profile:v high -pix_fmt yuv420p -g 30",
        "bitrateOpts": {
            "cbr": "-rc cbr -b:v <CONST_BITRATE_VALUE> -preset p6 ",
            "vbr": "-preset p7 -tune hq -rc constqp -qp <QP_VALUE> -rc-lookahead 20 -spatial_aq 1 -aq-strength 15 -b:v 0"
        },
        "cqpValues": {
            "High": [
                18
            ],
            "Mid": [
                25
            ],
            "Low": [
                28
            ]
        },
        "ext": [
            "mp4",
            "mkv",
            "mov"
        ],
        "maxBitRate": 2000,
        "os": "windows|linux",
        "device": "nvidia|tesla",
        "minSize": [
            145,
            145
        ],
        "maxSize": [
            4096,
            4096
        ],
        "maxBitDepth": 8
    },
    {
        "id": "h265-main-win-nvidia",
        "encoder": "H265",
        "profile": "Main",
        "allowsAlpha": 0,
        "gpu": "nvidia",
        "ffmpegOpts": "-c:v hevc_nvenc -profile:v main -pix_fmt yuv420p -b_ref_mode disabled -tag:v hvc1 -g 30",
        "bitrateOpts": {
            "cbr": "-rc cbr -b:v <CONST_BITRATE_VALUE> -preset p6",
            "vbr": "-preset p7 -tune hq -rc constqp -qp <QP_VALUE> -rc-lookahead 20 -spatial_aq 1 -aq-strength 15 -b:v 0"
        },
        "cqpValues": {
            "High": [
                17
            ],
            "Mid": [
                25
            ],
            "Low": [
                28
            ]
        },
        "ext": [
            "mp4",
            "mkv",
            "mov"
        ],
        "maxBitRate": 2000,
        "os": "windows|linux",
        "device": "nvidia|tesla",
        "minSize": [
            129,
            129
        ],
        "maxSize": [
            8192,
            8192
        ],
        "maxBitDepth": 12
    },
    {
        "id": "h265-main10-win-nvidia",
        "encoder": "H265",
        "profile": "Main10",
        "allowsAlpha": 0,
        "gpu": "nvidia",
        "ffmpegOpts": "-c:v hevc_nvenc -profile:v main10 -pix_fmt p010le -b_ref_mode disabled -tag:v hvc1 -g 30",
        "bitrateOpts": {
            "cbr": "-rc cbr -b:v <CONST_BITRATE_VALUE> -preset p6",
            "vbr": "-preset p7 -tune hq -rc constqp -qp <QP_VALUE> -rc-lookahead 20 -spatial_aq 1 -aq-strength 15 -b:v 0"
        },
        "cqpValues": {
            "High": [
                17
            ],
            "Mid": [
                25
            ],
            "Low": [
                28
            ]
        },
        "ext": [
            "mp4",
            "mkv",
            "mov"
        ],
        "maxBitRate": 2000,
        "os": "windows|linux",
        "device": "nvidia|tesla",
        "minSize": [
            129,
            129
        ],
        "maxSize": [
            8192,
            8192
        ],
        "maxBitDepth": 12
    },
    {
        "id": "h264-high-win-intel",
        "encoder": "H264",
        "profile": "High",
        "allowsAlpha": 0,
        "ffmpegOpts": "-c:v h264_qsv -profile:v high -preset medium -max_frame_size 65534 -pix_fmt nv12 -g 30",
        "ext": [
            "mp4",
            "mkv",
            "mov"
        ],
        "autoBitsPerPixel": "1.0",
        "maxBitRate": 2000,
        "os": "windows",
        "device": "intel",
        "minSize": [
            17,
            17
        ],
        "maxSize": [
            3840,
            2160
        ]
    },
    {
        "id": "h265-main-win-intel",
        "encoder": "H265",
        "profile": "Main",
        "allowsAlpha": 0,
        "ffmpegOpts": "-c:v hevc_qsv -profile:v main -preset medium -max_frame_size 65534 -pix_fmt nv12 -g 30",
        "ext": [
            "mp4",
            "mkv",
            "mov"
        ],
        "autoBitsPerPixel": "0.8",
        "maxBitRate": 2000,
        "os": "windows",
        "device": "intel",
        "minSize": [
            1,
            1
        ],
        "maxSize": [
            15360,
            8640
        ]
    },
    {
        "id": "h265-main10-win-intel",
        "encoder": "H265",
        "profile": "Main10",
        "allowsAlpha": 0,
        "ffmpegOpts": "-c:v hevc_qsv -profile:v main10 -preset medium -max_frame_size 65534 -pix_fmt p010le -g 30",
        "ext": [
            "mp4",
            "mkv",
            "mov"
        ],
        "autoBitsPerPixel": "1.0",
        "maxBitRate": 2000,
        "os": "windows",
        "device": "intel",
        "minSize": [
            1,
            1
        ],
        "maxSize": [
            15360,
            8640
        ]
    },
    {
        "id": "av1-win-nvidia",
        "encoder": "AV1",
        "profile": "8-bit",
        "allowsAlpha": 0,
        "gpu": "nvidia",
        "ffmpegOpts": "-c:v av1_nvenc -preset p7 -pix_fmt yuv420p",
        "bitrateOpts": {
            "cbr": "-rc cbr -b:v <CONST_BITRATE_VALUE> -preset p7",
            "vbr": "-preset p7 -tune hq -cq <QP_VALUE> -rc-lookahead 20 -spatial_aq 1 -aq-strength 1 -b:v 0"
        },
        "cqpValues": {
            "High": [
                23
            ],
            "Mid": [
                31
            ],
            "Low": [
                40
            ]
        },
        "ext": [
            "mp4",
            "webm",
            "mkv"
        ],
        "os": "windows|linux",
        "device": "nvidia",
        "maxBitRate": 800,
        "minSize": [
            1,
            1
        ],
        "maxSize": [
            16384,
            8704
        ],
        "maxBitDepth": 12,
        "compute": 809
    },
    {
        "id": "av1-10bit-win-nvidia",
        "encoder": "AV1",
        "profile": "10-bit",
        "allowsAlpha": 0,
        "gpu": "nvidia",
        "ffmpegOpts": "-c:v av1_nvenc -preset p7 -pix_fmt p010le",
        "bitrateOpts": {
            "cbr": "-rc cbr -b:v <CONST_BITRATE_VALUE> -preset p7",
            "vbr": "-preset p7 -tune hq -cq <QP_VALUE> -rc-lookahead 20 -spatial_aq 1 -aq-strength 1 -b:v 0"
        },
        "cqpValues": {
            "High": [
                20
            ],
            "Mid": [
                28
            ],
            "Low": [
                33
            ]
        },
        "ext": [
            "mp4",
            "webm",
            "mkv"
        ],
        "os": "windows|linux",
        "device": "nvidia",
        "maxBitRate": 800,
        "minSize": [
            1,
            1
        ],
        "maxSize": [
            16384,
            8704
        ],
        "maxBitDepth": 12,
        "compute": 809
    },
    {
        "id": "ffv1-8bit-420",
        "encoder": "FFV1",
        "profile": "8-bit 4:2:0",
        "allowsAlpha": 0,
        "ffmpegOpts": "-level 3 -c:v ffv1 -pix_fmt yuv420p -slices 9 -slicecrc 1 -g 1",
        "ext": [
            "mkv",
            "mov",
            "avi"
        ]
    },
    {
        "id": "ffv1-10bit-420",
        "encoder": "FFV1",
        "profile": "10-bit 4:2:0",
        "allowsAlpha": 0,
        "ffmpegOpts": "-level 3 -c:v ffv1 -pix_fmt yuv420p10le -slices 9 -slicecrc 1 -g 1",
        "ext": [
            "mkv",
            "mov",
            "avi"
        ]
    },
    {
        "id": "ffv1-12bit-420",
        "encoder": "FFV1",
        "profile": "12-bit 4:2:0",
        "allowsAlpha": 0,
        "ffmpegOpts": "-level 3 -c:v ffv1 -pix_fmt yuv420p12le -slices 9 -slicecrc 1 -g 1",
        "ext": [
            "mkv",
            "mov",
            "avi"
        ]
    },
    {
        "id": "ffv1-8bit-422",
        "encoder": "FFV1",
        "profile": "8-bit 4:2:2",
        "allowsAlpha": 0,
        "ffmpegOpts": "-level 3 -c:v ffv1 -pix_fmt yuv422p -slices 9 -slicecrc 1 -g 1",
        "ext": [
            "mkv",
            "mov",
            "avi"
        ]
    },
    {
        "id": "ffv1-10bit-422",
        "encoder": "FFV1",
        "profile": "10-bit 4:2:2",
        "allowsAlpha": 0,
        "ffmpegOpts": "-level 3 -c:v ffv1 -pix_fmt yuv422p10le -slices 9 -slicecrc 1 -g 1",
        "ext": [
            "mkv",
            "mov",
            "avi"
        ]
    },
    {
        "id": "ffv1-12bit-422",
        "encoder": "FFV1",
        "profile": "12-bit 4:2:2",
        "allowsAlpha": 0,
        "ffmpegOpts": "-level 3 -c:v ffv1 -pix_fmt yuv422p12le -slices 9 -slicecrc 1 -g 1",
        "ext": [
            "mkv",
            "mov",
            "avi"
        ]
    },
    {
        "id": "ffv1-8bit-444",
        "encoder": "FFV1",
        "profile": "8-bit 4:4:4",
        "allowsAlpha": 0,
        "ffmpegOpts": "-level 3 -c:v ffv1 -pix_fmt yuv444p -slices 9 -slicecrc 1 -g 1",
        "ext": [
            "mkv",
            "mov",
            "avi"
        ]
    },
    {
        "id": "ffv1-10bit-444",
        "encoder": "FFV1",
        "profile": "10-bit 4:4:4",
        "allowsAlpha": 0,
        "ffmpegOpts": "-level 3 -c:v ffv1 -pix_fmt yuv444p10le -slices 9 -slicecrc 1 -g 1",
        "ext": [
            "mkv",
            "mov",
            "avi"
        ]
    },
    {
        "id": "ffv1-12bit-444",
        "encoder": "FFV1",
        "profile": "12-bit 4:4:4",
        "allowsAlpha": 0,
        "ffmpegOpts": "-level 3 -c:v ffv1 -pix_fmt yuv444p12le -slices 9 -slicecrc 1 -g 1",
        "ext": [
            "mkv",
            "mov",
            "avi"
        ]
    },
    {
        "id": "vp9-good",
        "encoder": "VP9",
        "profile": "Good",
        "allowsAlpha": 0,
        "ffmpegOpts": "-strict experimental -c:v libvpx-vp9 -pix_fmt yuv420p -row-mt 1 -deadline good",
        "ext": [
            "mp4",
            "mkv",
            "webm"
        ],
        "maxBitRate": 2000,
        "minSize": [
            1,
            1
        ],
        "maxSize": [
            15360,
            8640
        ],
        "maxBitDepth": 12
    },
    {
        "id": "vp9-best",
        "encoder": "VP9",
        "profile": "Best",
        "allowsAlpha": 0,
        "ffmpegOpts": "-strict experimental -c:v libvpx-vp9 -pix_fmt yuv420p -row-mt 1 -deadline best",
        "ext": [
            "mp4",
            "mkv",
            "webm"
        ],
        "maxBitRate": 2000,
        "minSize": [
            1,
            1
        ],
        "maxSize": [
            15360,
            8640
        ],
        "maxBitDepth": 12
    },
    {
        "id": "QuickTime-v210",
        "encoder": "QuickTime V210",
        "shortName": "QT V210",
        "profile": "Uncompressed YUV 10-bit 4:2:2",
        "allowsAlpha": 0,
        "ffmpegOpts": "-c:v v210 -pix_fmt yuv422p10le",
        "ext": [
            "mov",
            "mkv",
            "avi"
        ]
    },
    {
        "id": "QuickTime-r210",
        "encoder": "QuickTime R210",
        "shortName": "QT R210",
        "profile": "Uncompressed RGB 10-bit",
        "allowsAlpha": 0,
        "ffmpegOpts": "-c:v r210 -pix_fmt gbrp10le",
        "ext": [
            "mov",
            "mkv",
            "avi"
        ]
    },
    {
        "id": "QTRLE",
        "encoder": "QuickTime Animation",
        "shortName": "QT Animation",
        "profile": "Run-length compressed RGB 8-bit",
        "allowsAlpha": 1,
        "ffmpegOpts": "-c:v qtrle -pix_fmt rgb24",
        "ext": [
            "mov"
        ]
    },
    {
        "id": "tiff-8bit",
        "encoder": "TIFF",
        "profile": "8-bit",
        "allowsAlpha": 1,
        "ffmpegOpts": "-c:v tiff -pix_fmt rgb24 -compression_algo deflate",
        "ext": [
            "tiff"
        ],
        "isImage": true
    },
    {
        "id": "tiff-16bit",
        "encoder": "TIFF",
        "profile": "16-bit",
        "allowsAlpha": 1,
        "ffmpegOpts": "-c:v tiff -pix_fmt rgb48le -compression_algo deflate",
        "ext": [
            "tiff"
        ],
        "isImage": true
    },
    {
        "id": "png-8bit",
        "encoder": "PNG",
        "profile": "8-bit",
        "allowsAlpha": 1,
        "ffmpegOpts": "-c:v png -pix_fmt rgb24",
        "ext": [
            "png"
        ],
        "isImage": true
    },
    {
        "id": "png-16bit",
        "encoder": "PNG",
        "profile": "16-bit",
        "allowsAlpha": 1,
        "ffmpegOpts": "-c:v png -pix_fmt rgb48be",
        "ext": [
            "png"
        ],
        "isImage": true
    },
    {
        "id": "jpeg-8bit",
        "encoder": "JPEG",
        "profile": "8-bit",
        "allowsAlpha": 0,
        "ffmpegOpts": "-pix_fmt rgb24 -q:v 2",
        "ext": [
            "jpg"
        ],
        "isImage": true
    },
    {
        "id": "exr",
        "encoder": "EXR",
        "allowsAlpha": 0,
        "ffmpegOpts": "-q:v 2",
        "ext": [
            "exr"
        ],
        "isImage": true
    },
    {
        "id": "dpx-10",
        "encoder": "DPX",
        "allowsAlpha": 0,
        "ffmpegOpts": "-c:v dpx -pix_fmt gbrp10le",
        "profile": "10-bit",
        "ext": [
            "dpx"
        ],
        "isImage": true
    },
    {
        "id": "dpx-12",
        "encoder": "DPX",
        "allowsAlpha": 0,
        "ffmpegOpts": "-c:v dpx -pix_fmt gbrp12le",
        "profile": "12-bit",
        "ext": [
            "dpx"
        ],
        "isImage": true
    }
]''')

CODEC_OPTIONS_DICT = {}
for enc in RAW_ENCODERS_DATA:
    if 'bitrateOpts' in enc and 'cbr' not in enc['bitrateOpts']:
        continue
    if 'os' in enc and 'windows' not in enc['os']:
        continue
    CODEC_OPTIONS_DICT[enc['id']] = enc

CODEC_OPTIONS = list(CODEC_OPTIONS_DICT.keys()) if CODEC_OPTIONS_DICT else ["h265-main10-win-nvidia"]
DEFAULT_CODEC = "h265-main10-win-nvidia"
if DEFAULT_CODEC not in CODEC_OPTIONS:
    DEFAULT_CODEC = CODEC_OPTIONS[0]

def get_codec_opts(out_codec, bitrate, include_audio=False):
    opts = ["-fps_mode", "cfr"]
    
    if out_codec in CODEC_OPTIONS_DICT:
        enc = CODEC_OPTIONS_DICT[out_codec]
        ffmpeg_opts = enc.get('ffmpegOpts', '')
        if ffmpeg_opts:
            opts.extend(ffmpeg_opts.split())
        
        if 'bitrateOpts' in enc and 'cbr' in enc['bitrateOpts']:
            cbr_opts = enc['bitrateOpts']['cbr'].replace("<CONST_BITRATE_VALUE>", bitrate)
            opts.extend(cbr_opts.split())
    else:
        opts.extend(["-c:v", "hevc_nvenc", "-profile:v", "main10", "-pix_fmt", "p010le", "-b_ref_mode", "disabled", "-tag:v", "hvc1", "-g", "20", "-rc", "cbr", "-b:v", bitrate, "-maxrate", bitrate, "-bufsize", bitrate])
        
    if include_audio:
        opts.extend(["-c:a", "aac", "-b:a", "256k"])
        
    opts.extend(["-avoid_negative_ts", "make_zero", "-fflags", "+genpts"])
    return opts

def get_ext_from_codec(out_codec, original_ext):
    if out_codec in CODEC_OPTIONS_DICT:
        return "." + CODEC_OPTIONS_DICT[out_codec].get("ext", [original_ext.lstrip('.')])[0]
    return original_ext

def split_video(input_path, mode, output_dir, conversion="none", log_callback=None, process_callback=None, bitrate="100M", fps=None, height=None, width=None, out_codec="h265-main10-win-nvidia"):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    fps = frame_rate(input_path) if not have(fps) else fps
    filename = os.path.splitext(os.path.basename(input_path))[0]
    ext = os.path.splitext(input_path)[1]
    ext = get_ext_from_codec(out_codec, ext)
    width = 'iw' if not have(width) else width
    height = 'ih' if not have(height) else height    
    
    if log_callback: log_callback(f"Detecting codec for {input_path}...")
    codec = vcodec(input_path)
    w_in, h_in = vresolution(input_path)
    wi, hi = w_in, h_in

    if mode in ('left_and_right', 'left', 'right'):
        wi = w_in // 2 if w_in > 0 else 0
    elif mode in ('top_and_bottom', 'top', 'bottom'):
        wi = w_in // 2 if w_in > 0 else 0
        hi = h_in // 2 if h_in > 0 else 0
        
    dim_str = f":w={wi}:h={hi}" if wi > 0 and hi > 0 else ""

    decoder_opts = []
    if codec == 'h264':
        decoder_opts = ["-hwaccel", "cuda", "-c:v", "h264_cuvid"]
    elif codec == 'hevc':
        decoder_opts = ["-hwaccel", "cuda", "-c:v", "hevc_cuvid"]

    v360_filter = ""
    fisheye_suffix = ""
    if conversion == "to_fisheye":
        v360_filter = f",v360=hequirect:fisheye{dim_str}"
        fisheye_suffix = "_FE180"
    elif conversion == "to_fisheye190":
        v360_filter = f",v360=hequirect:fisheye:d_fov=190{dim_str}"
        fisheye_suffix = "_FE190"        
    elif conversion == "to_hequirect":
        v360_filter = f",v360=fisheye:hequirect{dim_str}"
        fisheye_suffix = "_180"
    elif conversion == "heq_to_flat":
        v360_filter = f",v360=hequirect:sg:v_fov=60:h_fov=60{dim_str}"
        fisheye_suffix = "_flat"
    elif conversion == "fish_to_flat":
        v360_filter = f",v360=fisheye:sg:v_fov=60:h_fov=60{dim_str}"
        fisheye_suffix = "_flat"
    
    if mode == 'left_and_right':

        output_left = os.path.join(output_dir, f"{filename}_L{fisheye_suffix}{ext}")
        output_right = os.path.join(output_dir, f"{filename}_R{fisheye_suffix}{ext}")

        filter_complex = f"[0:v]fps={fps},setpts=N/({fps}*TB),split=2[v1][v2];[v1]crop=iw/2:ih:0:0{v360_filter},scale=w={width}:h={height}:flags=bicubic[left];[v2]crop=iw/2:ih:iw/2:0{v360_filter},scale=w={width}:h={height}:flags=bicubic[right]"
        
        cmd = ["ffmpeg", "-hide_banner", "-y"]
        cmd.extend(decoder_opts)
        cmd.extend(["-i", input_path])
        cmd.extend(["-sws_flags", "bicubic+full_chroma_int+accurate_rnd+full_chroma_inp"])
        cmd.extend(["-filter_complex", filter_complex])
        cmd.extend(["-map", "[left]", "-map", "0:a:?"])
        cmd.extend(get_codec_opts(out_codec, bitrate, include_audio=True))
        cmd.extend(["-movflags", "+faststart+write_colr+use_metadata_tags"])
        cmd.extend([output_left])

        cmd.extend(["-map", "[right]", "-map", "0:a:?"])
        cmd.extend(get_codec_opts(out_codec, bitrate, include_audio=True))
        cmd.extend(["-movflags", "+faststart+write_colr+use_metadata_tags"])
        cmd.extend([output_right])
        
        if log_callback: log_callback(f"Starting split (left_and_right, conv={conversion}) for {input_path}...")
        run_process(cmd, log_callback, process_callback)
        return output_left, output_right
        
    elif mode == 'top_and_bottom':
        output_top = os.path.join(output_dir, f"{filename}_T{fisheye_suffix}{ext}")
        output_bottom = os.path.join(output_dir, f"{filename}_B{fisheye_suffix}{ext}")

        filter_complex = f"[0:v]fps={fps},setpts=N/({fps}*TB),split=2[v1][v2];[v1]crop=iw/2:ih/2:iw/4:0{v360_filter},scale=w={width}:h={height}:flags=bicubic[top];[v2]crop=iw/2:ih/2:iw/4:ih/2{v360_filter},scale=w={width}:h={height}:flags=bicubic[bottom]"
        
        cmd = ["ffmpeg", "-hide_banner", "-y"]
        cmd.extend(decoder_opts)
        cmd.extend(["-i", input_path])
        cmd.extend(["-sws_flags", "bicubic+full_chroma_int+accurate_rnd+full_chroma_inp"])
        cmd.extend(["-filter_complex", filter_complex])
        cmd.extend(["-map", "[top]", "-map", "0:a:?"])
        
        cmd.extend(get_codec_opts(out_codec, bitrate, include_audio=True))
        cmd.extend(["-movflags", "+faststart+write_colr+use_metadata_tags"])
        cmd.extend([output_top])
        cmd.extend(["-map", "[bottom]", "-map", "0:a:?"])

        cmd.extend(get_codec_opts(out_codec, bitrate, include_audio=True))
        cmd.extend(["-movflags", "+faststart+write_colr+use_metadata_tags"])
        cmd.extend([output_bottom])
        
        if log_callback: log_callback(f"Starting split (top_and_bottom, conv={conversion}) for {input_path}...")
        run_process(cmd, log_callback, process_callback)
        return output_top, output_bottom
        
    else:
        if mode == 'left':
            crop_filter = f"fps={fps},setpts=N/({fps}*TB),crop=iw/2:ih:0:0{v360_filter},scale=w={width}:h={height}:flags=bicubic"
            suffix = '_L'
        elif mode == 'right':
            crop_filter = f"fps={fps},setpts=N/({fps}*TB),crop=iw/2:ih:iw/2:0{v360_filter},scale=w={width}:h={height}:flags=bicubic"
            suffix = '_R' 
        elif mode == 'top':
            crop_filter = f"fps={fps},setpts=N/({fps}*TB),crop=iw/2:ih/2:iw/4:0{v360_filter},scale=w={width}:h={height}:flags=bicubic"
            suffix = '_T' 
        elif mode == 'bottom':
            crop_filter = f"fps={fps},setpts=N/({fps}*TB),crop=iw/2:ih/2:iw/4:ih/2{v360_filter},scale=w={width}:h={height}:flags=bicubic"
            suffix = '_B' 
        else:
            raise ValueError(f"Unknown split mode: {mode}")
        
        output_file = os.path.join(output_dir, f"{filename}{suffix}{fisheye_suffix}{ext}")
        
        cmd = ["ffmpeg", "-hide_banner", "-y"]
        cmd.extend(decoder_opts)
        cmd.extend(["-i", input_path])
        cmd.extend(["-vf", crop_filter])
        cmd.extend(["-c:a", "copy"])
        cmd.extend(get_codec_opts(out_codec, bitrate, include_audio=False))
        cmd.extend(["-movflags", "+faststart"])
        cmd.extend([output_file])

        if log_callback: log_callback(f"Starting split ({mode}, conv={conversion}) for {input_path}...")
        run_process(cmd, log_callback, process_callback)
        return output_file, output_file

def combine_video(input_path_1, input_path_2, mode, output_path, conversion="none", log_callback=None, process_callback=None, bitrate="100M", mask_path=None, fps=None, height=None, width=None, out_codec="h265-main10-win-nvidia"):
    if log_callback: log_callback(f"Combining {input_path_1} and {input_path_2} into {output_path} (Mode: {mode}, Conv: {conversion})")

    fps = frame_rate(input_path_1) if not have(fps) else fps
    codec1 = vcodec(input_path_1)
    w_in, h_in = vresolution(input_path_1)
    
    out_w = w_in * 2 if mode == "left_right" else w_in
    out_h = h_in * 2 if mode == "top_bottom" else h_in

    width = 'iw' if not have(width) else width
    height = 'ih' if not have(height) else height  
    
    dim_str = f":w={w_in}:h={h_in}" if w_in > 0 and h_in > 0 else ""

    input_opts_1 = []
    if codec1 == 'h264':
        input_opts_1 = ["-hwaccel", "cuda", "-c:v", "h264_cuvid"]
    elif codec1 == 'hevc':
        input_opts_1 = ["-hwaccel", "cuda", "-c:v", "hevc_cuvid"]
    
    cmd = ["ffmpeg", "-hide_banner", "-y"]
    cmd.extend(input_opts_1)
    cmd.extend(["-i", input_path_1])
    if mask_path is not None:
        cmd.extend(["-i", mask_path])
    cmd.extend(["-i", input_path_2])

    v360_filter = ""
    if conversion == "to_fisheye":
        v360_filter = f"v360=hequirect:fisheye{dim_str},"
    elif conversion == "to_fisheye190":
        v360_filter = f"v360=hequirect:fisheye:d_fov=190{dim_str},"
    elif conversion == "to_hequirect":
        v360_filter = f"v360=fisheye:hequirect{dim_str},"
    elif conversion == "heq_to_flat":
        v360_filter = f"v360=hequirect:sg:v_fov=60:h_fov=60{dim_str},"
    elif conversion == "fish_to_flat":
        v360_filter = f"v360=fisheye:sg:v_fov=60:h_fov=60{dim_str},"

    if mask_path is not None:
        idx2 = 2
    else:
        idx2 = 1

    if mode == 'left_right':
        base_filter = f"[0:v]{v360_filter}setpts=PTS-STARTPTS[left];[{idx2}:v]{v360_filter}setpts=PTS-STARTPTS[right];[left][right]hstack=inputs=2"
    elif mode == 'top_bottom':
        base_filter = f"[0:v]{v360_filter}setpts=PTS-STARTPTS[top];[{idx2}:v]{v360_filter}setpts=PTS-STARTPTS[bottom];[top][bottom]vstack=inputs=2"
    else:
        raise ValueError(f"Unknown combine mode: {mode}")

    if mask_path is not None:
        filter_complex = f"{base_filter}[stacked];[1:v][stacked]scale2ref[mask][stacked_ref];[stacked_ref][mask]overlay=0:0,fps={fps},setpts=N/({fps}*TB),scale=w={width}:h={height}:flags=bicubic[v]"
    else:
        filter_complex = f"{base_filter},fps={fps},setpts=N/({fps}*TB),scale=w={width}:h={height}:flags=bicubic[v]"

    cmd.extend(["-filter_complex", filter_complex])
    cmd.extend(["-map", "[v]", "-map", "0:a:?"])
    cmd.extend(["-c:a", "copy"])
    
    cmd.extend(get_codec_opts(out_codec, bitrate, include_audio=False))
    cmd.extend(["-movflags", "+faststart"])
    cmd.extend(["-color_range", "pc", "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709"])
    
    cmd.extend([output_path])

    run_process(cmd, log_callback, process_callback)
    return output_path

def tb_to_sbs(input_path, output_path, conversion="none", log_callback=None, process_callback=None, bitrate="100M", operation_mode="custom_tb_to_sbs", mask_path=None, fps=None, height=None, width=None, out_codec="h265-main10-win-nvidia"):
    if log_callback: log_callback(f"Converting video for {input_path} (conv={conversion}, op={operation_mode})")
    
    fps = frame_rate(input_path) if not have(fps) else fps
    codec = vcodec(input_path)
    w_in, h_in = vresolution(input_path)
    wi, hi = w_in, h_in
    if operation_mode == "sbs_to_sbs":
        wi = w_in // 2 if w_in > 0 else 0
    elif operation_mode in ("tb_to_tb", "tb_to_sbs"):
        wi = w_in // 2 if w_in > 0 else 0
        hi = h_in // 2 if h_in > 0 else 0
    elif operation_mode == "sbs_to_tb":
        wi = w_in // 2 if w_in > 0 else 0
    else: # custom_tb_to_sbs
        wi = w_in // 2 if w_in > 0 else 0
        hi = h_in // 2 if h_in > 0 else 0
        
    width = 'iw' if not have(width) else width
    height = 'ih' if not have(height) else height  

    dim_str = f":w={wi}:h={hi}" if wi > 0 and hi > 0 else ""

    decoder_opts = []
    if codec == 'h264':
        decoder_opts = ["-hwaccel", "cuda", "-c:v", "h264_cuvid"]
    elif codec == 'hevc':
        decoder_opts = ["-hwaccel", "cuda", "-c:v", "hevc_cuvid"]
        
    cmd = ["ffmpeg", "-hide_banner", "-y"]
    cmd.extend(decoder_opts)
    cmd.extend(["-i", input_path])
    if mask_path is not None:
        cmd.extend(["-i", mask_path])
    
    v360_filter = ""
    if conversion == "to_fisheye":
        v360_filter = f",v360=hequirect:fisheye{dim_str}"
    elif conversion == "to_fisheye190":
        v360_filter = f",v360=hequirect:fisheye:d_fov=190{dim_str}"
    elif conversion == "to_hequirect":
        v360_filter = f",v360=fisheye:hequirect{dim_str}"
    elif conversion == "heq_to_flat":
        v360_filter = f",v360=hequirect:sg:v_fov=60:h_fov=60{dim_str}"
    elif conversion == "fish_to_flat":
        v360_filter = f",v360=fisheye:sg:v_fov=60:h_fov=60{dim_str}"
        
    base_filter = ""
    if operation_mode == "sbs_to_sbs":
        base_filter = (
            f"[0:v]crop=iw/2:ih:0:0{v360_filter}[left];"
            f"[0:v]crop=iw/2:ih:iw/2:0{v360_filter}[right];"
            f"[left][right]hstack=inputs=2"
        )
    elif operation_mode == "tb_to_tb":
        base_filter = (
            f"[0:v]crop=iw/2:ih/2:iw/4:0{v360_filter}[top];"
            f"[0:v]crop=iw/2:ih/2:iw/4:ih/2{v360_filter}[bottom];"
            f"[top][bottom]vstack=inputs=2"
        )
    elif operation_mode == "tb_to_sbs":
        base_filter = (
            f"[0:v]crop=iw/2:ih/2:iw/4:0{v360_filter}[top];"
            f"[0:v]crop=iw/2:ih/2:iw/4:ih/2{v360_filter}[bottom];"
            f"[top][bottom]hstack=inputs=2"
        )
    elif operation_mode == "sbs_to_tb":
        base_filter = (
            f"[0:v]crop=iw/2:ih:0:0{v360_filter}[left];"
            f"[0:v]crop=iw/2:ih:iw/2:0{v360_filter}[right];"
            f"[left][right]vstack=inputs=2"
        )
    else: # custom_tb_to_sbs
        base_filter = (
            f"[0:v]crop=iw/2:ih/2:iw/4:0{v360_filter}[left];"
            f"[0:v]crop=iw/2:ih/2:iw/4:ih/2{v360_filter}[right];"
            f"[left][right]hstack=inputs=2"
        )

    if mask_path is not None:
        filter_complex = f"{base_filter}[stacked];[1:v][stacked]scale2ref[mask][stacked_ref];[stacked_ref][mask]overlay=0:0,fps={fps},setpts=N/({fps}*TB),scale=w={width}:h={height}:flags=bicubic[v]"
    else:
        filter_complex = f"{base_filter},fps={fps},setpts=N/({fps}*TB),scale=w={width}:h={height}:flags=bicubic[v]"
    
    cmd.extend(["-filter_complex", filter_complex])
    cmd.extend(["-map", "[v]", "-map", "0:a?", "-c:a", "copy"])
    
    cmd.extend(get_codec_opts(out_codec, bitrate, include_audio=False))
    cmd.extend(["-movflags", "+faststart"])

    cmd.extend(["-color_range", "pc", "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709"])
    
    cmd.extend([output_path])

    run_process(cmd, log_callback, process_callback)
    return output_path

def batch_tb_to_sbs(input_dir, output_dir=None, conversion="none", log_callback=None, process_callback=None, bitrate="100M", operation_mode="custom_tb_to_sbs", mask_path=None, fps=None, height=None, width=None, out_codec="h265-main10-win-nvidia"):
    width = 'iw' if not have(width) else width
    height = 'ih' if not have(height) else height  
    
    if log_callback: log_callback(f"Starting batch conversion in {input_dir}")
    mp4_files = glob.glob(os.path.join(input_dir, "*.mp4")) + glob.glob(os.path.join(input_dir, "*.mkv"))
    
    if not mp4_files:
        if log_callback: log_callback(f"No .mp4 or .mkv files found in {input_dir}")
        return False
        
    for input_path in mp4_files:
        if "_LR" in input_path or "_FE180" in input_path or "_FE190" in input_path or "_180" in input_path or ".restored" in input_path:
            continue
            
        filename = os.path.splitext(os.path.basename(input_path))[0]
        out_dir = output_dir if output_dir else input_dir
        
        suffix = ""
        if operation_mode in ("sbs_to_tb", "tb_to_tb"):
            suffix += "_TB"
        else:
            suffix += "_LR"
            
        if conversion == "to_fisheye":
            suffix = "_FE180" + suffix
        elif conversion == "to_fisheye190":
            suffix = "_FE190" + suffix
        elif conversion == "to_hequirect":
            suffix = "_180" + suffix
        elif conversion == "heq_to_flat" or conversion == "fish_to_flat":
            suffix = "_flat" + suffix
            
        ext_out = get_ext_from_codec(out_codec, ".mp4")
        output_path = os.path.join(out_dir, f"{filename}{suffix}{ext_out}")
        
        if os.path.exists(output_path):
            if log_callback: log_callback(f"Skipping {os.path.basename(input_path)}, output {os.path.basename(output_path)} already exists.")
            continue
            
        tb_to_sbs(input_path, output_path, conversion=conversion, log_callback=log_callback, process_callback=process_callback, bitrate=bitrate, operation_mode=operation_mode, mask_path=mask_path, fps=fps, height=height, width=width, out_codec=out_codec)
        
    if log_callback: log_callback("Batch conversion finished.")
    return output_dir if output_dir else input_dir

# -------------------------- COMFYUI NODE CLASSES --------------------------

class VRSplitVideo:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "input_video_path": ("STRING", {"default": ""}),
                "output_dir": ("STRING", {"default": ""}),
                "mode": (["left_and_right", "left", "right", "top_and_bottom", "top", "bottom"],),
                "conversion": (["none", "to_fisheye", "to_fisheye190", "to_hequirect", "heq_to_flat", "fish_to_flat"],),
                "bitrate": ("STRING", {"default": "100M"}),
                "out_codec": (CODEC_OPTIONS,),
            },
            "optional": {
                "fps": ("STRING", {"default": ""}),
                "width": ("STRING", {"default": ""}),
                "height": ("STRING", {"default": ""}),
            }
        }
        
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("out_path_1", "out_path_2")
    FUNCTION = "process"
    CATEGORY = "VR/Video"

    def process(self, input_video_path, output_dir, mode, conversion, bitrate, out_codec, fps="", width="", height=""):
        if not input_video_path or not os.path.exists(input_video_path):
            raise ValueError(f"Input file not found: {input_video_path}")
            
        if not output_dir:
            output_dir = os.path.dirname(input_video_path)
            
        out1, out2 = split_video(
            input_video_path, 
            mode, 
            output_dir, 
            conversion=conversion, 
            bitrate=bitrate, 
            fps=fps if fps else None, 
            height=height if height else None, 
            width=width if width else None, 
            out_codec=out_codec
        )
        return (out1, out2)

class VRCombineVideo:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "input_video_1": ("STRING", {"default": ""}),
                "input_video_2": ("STRING", {"default": ""}),
                "output_path": ("STRING", {"default": ""}),
                "mode": (["left_right", "top_bottom"],),
                "conversion": (["none", "to_fisheye", "to_fisheye190", "to_hequirect", "heq_to_flat", "fish_to_flat"],),
                "bitrate": ("STRING", {"default": "100M"}),
                "out_codec": (CODEC_OPTIONS,),
            },
            "optional": {
                "mask_image_path": ("STRING", {"default": ""}),
                "fps": ("STRING", {"default": ""}),
                "width": ("STRING", {"default": ""}),
                "height": ("STRING", {"default": ""}),
            }
        }
        
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("output_video_path",)
    FUNCTION = "process"
    CATEGORY = "VR/Video"

    def process(self, input_video_1, input_video_2, output_path, mode, conversion, bitrate, out_codec, mask_image_path="", fps="", width="", height=""):
        if not input_video_1 or not os.path.exists(input_video_1):
            raise ValueError(f"Input file 1 not found: {input_video_1}")
        if not input_video_2 or not os.path.exists(input_video_2):
            raise ValueError(f"Input file 2 not found: {input_video_2}")

        if not output_path:
            dirname = os.path.dirname(input_video_1)
            filename = os.path.splitext(os.path.basename(input_video_1))[0]
            for s in ["_L", "_R", "_T", "_B", "_l", "_r", "_t", "_b"]:
                if filename.endswith(s):
                    filename = filename[:-len(s)]
                    break
            
            suffix = "_LR" if mode == "left_right" else "_TB"
            ext_out = get_ext_from_codec(out_codec, ".mp4")
            output_path = os.path.join(dirname, f"{filename}{suffix}{ext_out}")

        mask_val = mask_image_path if mask_image_path and os.path.exists(mask_image_path) else None
        
        out = combine_video(
            input_video_1, 
            input_video_2, 
            mode, 
            output_path, 
            conversion=conversion, 
            bitrate=bitrate, 
            mask_path=mask_val, 
            fps=fps if fps else None, 
            height=height if height else None, 
            width=width if width else None, 
            out_codec=out_codec
        )
        return (out,)

class VRConvertVideo:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "input_path_or_dir": ("STRING", {"default": ""}),
                "output_path_or_dir": ("STRING", {"default": ""}),
                "operation_mode": (["custom_tb_to_sbs", "sbs_to_sbs", "tb_to_tb", "tb_to_sbs", "sbs_to_tb"],),
                "conversion": (["none", "to_fisheye", "to_fisheye190", "to_hequirect", "heq_to_flat", "fish_to_flat"],),
                "bitrate": ("STRING", {"default": "100M"}),
                "out_codec": (CODEC_OPTIONS,),
            },
            "optional": {
                "mask_image_path": ("STRING", {"default": ""}),
                "fps": ("STRING", {"default": ""}),
                "width": ("STRING", {"default": ""}),
                "height": ("STRING", {"default": ""}),
            }
        }
        
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("output_path",)
    FUNCTION = "process"
    CATEGORY = "VR/Video"

    def process(self, input_path_or_dir, output_path_or_dir, operation_mode, conversion, bitrate, out_codec, mask_image_path="", fps="", width="", height=""):
        if not input_path_or_dir or not os.path.exists(input_path_or_dir):
            raise ValueError(f"Input file or directory not found: {input_path_or_dir}")

        mask_val = mask_image_path if mask_image_path and os.path.exists(mask_image_path) else None

        if os.path.isdir(input_path_or_dir):
            output_dir = output_path_or_dir if output_path_or_dir and os.path.isdir(output_path_or_dir) else None
            out = batch_tb_to_sbs(
                input_path_or_dir,
                output_dir=output_dir,
                conversion=conversion,
                bitrate=bitrate,
                operation_mode=operation_mode,
                mask_path=mask_val,
                fps=fps if fps else None,
                width=width if width else None,
                height=height if height else None,
                out_codec=out_codec
            )
            return (out,)
        else:
            out_file = output_path_or_dir
            if not out_file or os.path.isdir(out_file):
                dirname = out_file if out_file else os.path.dirname(input_path_or_dir)
                filename = os.path.splitext(os.path.basename(input_path_or_dir))[0]
                suffix = ""
                if operation_mode in ("sbs_to_tb", "tb_to_tb"):
                    suffix += "_TB"
                else:
                    suffix += "_LR"

                if conversion == "to_fisheye":
                    suffix = "_FE180" + suffix
                elif conversion == "to_fisheye190":
                    suffix = "_FE190" + suffix
                elif conversion == "to_hequirect":
                    suffix = "_180" + suffix
                elif conversion == "heq_to_flat" or conversion == "fish_to_flat":
                    suffix = "_flat" + suffix
                    
                ext_out = get_ext_from_codec(out_codec, ".mp4")
                out_file = os.path.join(dirname, f"{filename}{suffix}{ext_out}")

            out = tb_to_sbs(
                input_path_or_dir,
                out_file,
                conversion=conversion,
                bitrate=bitrate,
                operation_mode=operation_mode,
                mask_path=mask_val,
                fps=fps if fps else None,
                width=width if width else None,
                height=height if height else None,
                out_codec=out_codec
            )
            return (out,)

NODE_CLASS_MAPPINGS = {
    "VRSplitVideo": VRSplitVideo,
    "VRCombineVideo": VRCombineVideo,
    "VRConvertVideo": VRConvertVideo
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "VRSplitVideo": "VR Split Video",
    "VRCombineVideo": "VR Combine Video",
    "VRConvertVideo": "VR Convert Video"
}
