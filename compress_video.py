import ffmpeg

#inorder to use the below function install ffmpeg folder and it should be available in the environment


def compress_video(video_bytes: bytes, output_format='mkv', target_size_MB=10) -> bytes:
    # Set the target size in bytes
    target_size_bytes = target_size_MB * 1024 * 1024

    # Input video stream
    input_stream = ffmpeg.input('pipe:0')

    # Use constant rate factor (CRF) for video compression
    # Adjust the crf value as needed (lower values mean higher quality but larger file size)
    ffmpeg_cmd = (
        ffmpeg.output(input_stream, 'pipe:1', vf='scale=trunc(iw/2)*2:trunc(ih/2)*2', crf=23, format=output_format)
        .global_args('-loglevel', 'error', '-ffmpeg', 'C:\\path\\to\\ffmpeg.exe')
        .run_async(pipe_stdin=True, pipe_stdout=True, pipe_stderr=True)
    )

    # Write video bytes to the stdin of the ffmpeg process
    ffmpeg_cmd.communicate(input=video_bytes)

    # Get the compressed video bytes from stdout
    compressed_video_bytes = ffmpeg_cmd.stdout.read()

    return compressed_video_bytes
