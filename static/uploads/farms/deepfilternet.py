import soundfile as sf
import numpy as np
import librosa
import torch
from df.enhance import enhance, init_df


def calculate_metrics(original, processed):
    min_len = min(len(original), len(processed))
    original = original[:min_len]
    processed = processed[:min_len]
    noise = original - processed

    noise_power = np.mean(noise ** 2) + 1e-10
    orig_power = np.mean(original ** 2) + 1e-10
    proc_power = np.mean(processed ** 2) + 1e-10

    snr_before = 10 * np.log10(orig_power / noise_power)
    snr_after = 10 * np.log10(proc_power / noise_power)

    # 전체 노이즈 대비 잔류 소음 비율
    total_noise_power = np.mean(original ** 2) + 1e-10  # 기준: 원본 - 무음
    residue_ratio = (noise_power / total_noise_power) * 100

    return {
        'SNR_개선(dB)': snr_after - snr_before,
        '원본_RMS': np.sqrt(orig_power),
        '처리후_RMS': np.sqrt(proc_power),
        '제거된_소음_RMS': np.sqrt(noise_power),
        '잔류소음_비율(%)': residue_ratio
    }


def process_audio_files(file_list):
    model, df_state, _ = init_df()

    results = {}
    for file in file_list:
        audio, sr = librosa.load(file, sr=48000)
        audio_tensor = torch.from_numpy(audio).float().unsqueeze(0)  # (T,) → (1, T)

        processed_tensor = enhance(
            model,
            df_state,
            audio_tensor,
            atten_lim_db=100.0
        )

        processed = processed_tensor.squeeze(0).cpu().numpy()  # (1, T) → (T,)
        sf.write(f'cleaned_{file}', processed, sr)
        results[file] = calculate_metrics(audio, processed)
    return results


if __name__ == "__main__":
    input_files = ['noisy_input.wav']
    processing_results = process_audio_files(input_files)

    for file, metrics in processing_results.items():
        print(f"\n📊 {file} 분석 결과:")
        print(f"- SNR 개선량: {metrics['SNR_개선(dB)']:.2f} dB")
        print(f"- 원본 신호 강도: {metrics['원본_RMS']:.4f}")
        print(f"- 처리 후 신호 강도: {metrics['처리후_RMS']:.4f}")
        print(f"- 제거된 소음 레벨: {metrics['제거된_소음_RMS']:.4f}")
        print(f"- 잔류 소음 비율: {metrics['잔류소음_비율(%)']:.2f}%")
