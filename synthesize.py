import numpy as np
import tensorflow as tf
import argparse
from midi_ddsp.utils.midi_synthesis_utils import synthesize_mono_midi, conditioning_df_to_audio
from midi_ddsp.utils.inference_utils import get_process_group
from midi_ddsp.midi_ddsp_synthesize import load_pretrained_model
from midi_ddsp.data_handling.instrument_name_utils import INST_NAME_TO_ID_DICT
from pitch_shift_for_instruments import get_optimal_pitch_shift
import soundfile as sf
import os

def main():
  parser = argparse.ArgumentParser(description='Synthesize MIDI file using MIDI-DDSP')
  parser.add_argument('--midi_file', type=str, required=True, help='Path to input MIDI file')
  parser.add_argument('--instrument', type=str, default='violin', 
                     choices=['violin', 'viola', 'cello', 'double_bass', 'flute', 'oboe', 
                             'clarinet', 'saxophone', 'bassoon', 'trumpet', 'horn', 
                             'trombone', 'tuba', 'guitar'],
                     help='Instrument name to synthesize with')
  parser.add_argument('--auto-octave-shift', action='store_true', default=False, help='Auto octave shift for each instrument\'s pitch range; if True, the pitch offset will be automatically calculated based on the instrument\'s pitch range and `pitch_offset` will be ignored')
  parser.add_argument('--pitch_offset', type=int, default=0, help='Pitch offset in semitones')
  parser.add_argument('--output_dir', type=str, default=None, help='Output directory for saving files')
  args = parser.parse_args()

  # Load pre-trained model
  synthesis_generator, expression_generator = load_pretrained_model()

  # Get instrument ID
  instrument_id = INST_NAME_TO_ID_DICT[args.instrument]

  if args.auto_octave_shift:
    # Get instrument's pitch range
    pitch_offset = get_optimal_pitch_shift(args.midi_file, args.instrument)
  else:
    pitch_offset = args.pitch_offset

  # Run model prediction
  midi_audio, midi_control_params, midi_synth_params, conditioning_df = synthesize_mono_midi(
    synthesis_generator,
    expression_generator,
    args.midi_file,
    instrument_id,
    pitch_offset=pitch_offset,
    output_dir=None
  )

  midi_audio = midi_audio[0].numpy()
  
  # Normalize audio to [-1, 1] range
  midi_audio = midi_audio / np.max(np.abs(midi_audio))

  if args.output_dir is None:
    output_path = f"{args.midi_file.split('/')[-1].split('.')[0]}_{args.instrument}_{pitch_offset}.wav"
  else:
    os.makedirs(args.output_dir, exist_ok=True)
    output_path = os.path.join(args.output_dir, f"{args.midi_file.split('/')[-1].split('.')[0]}_{args.instrument}_{pitch_offset}.wav")
  # Save audio
  sf.write(output_path, midi_audio, 16000)

if __name__ == '__main__':
  main()
