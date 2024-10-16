from moviepy.editor import *

def create_animation(image_folder, output_video, fps=24):
    """
    Create a basic animation by stitching images together into a video.
    """
    try:
        image_files = [os.path.join(image_folder, img) for img in sorted(os.listdir(image_folder)) if img.endswith(".png") or img.endswith(".jpg")]
        clips = [ImageClip(m).set_duration(1/fps) for m in image_files]
        video = concatenate_videoclips(clips, method="compose")
        video.write_videofile(output_video, fps=fps)
        print(f"Animation created and saved at {output_video}")
    except Exception as e:
        print(f"Error creating animation: {e}")

def add_audio_to_animation(animation_file, audio_file, output_file):
    """
    Add an audio track to an animation.
    """
    try:
        video = VideoFileClip(animation_file)
        audio = AudioFileClip(audio_file)
        final_video = video.set_audio(audio)
        final_video.write_videofile(output_file, fps=24)
        print(f"Animation with audio saved at {output_file}")
    except Exception as e:
        print(f"Error adding audio to animation: {e}")

def merge_videos(video1_path, video2_path, output_path):
    """
    Merge two video clips into one.
    """
    try:
        clip1 = VideoFileClip(video1_path)
        clip2 = VideoFileClip(video2_path)
        final_clip = concatenate_videoclips([clip1, clip2])
        final_clip.write_videofile(output_path)
        print(f"Videos merged and saved at {output_path}")
    except Exception as e:
        print(f"Error merging videos: {e}")
