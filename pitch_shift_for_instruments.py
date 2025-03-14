import pretty_midi

INST_PITCH_RANGE_DICT = {
    'violin': {'min': 55, 'max': 100},  # G3 to E7
    'viola': {'min': 48, 'max': 93},    # C3 to A6
    'cello': {'min': 36, 'max': 84},    # C2 to C6
    'double_bass': {'min': 28, 'max': 67},  # E1 to G4
    'flute': {'min': 60, 'max': 98},    # C4 to D7
    'oboe': {'min': 58, 'max': 91},     # Bb3 to G6
    'clarinet': {'min': 50, 'max': 91},  # D3 to G6
    'saxophone': {'min': 49, 'max': 80},  # Db3 to Ab5 (Alto Sax)
    'bassoon': {'min': 34, 'max': 76},  # Bb1 to E5
    'trumpet': {'min': 54, 'max': 86},  # F#3 to D6
    'horn': {'min': 36, 'max': 77},     # C2 to F5
    'trombone': {'min': 40, 'max': 82}, # E2 to Bb5
    'tuba': {'min': 26, 'max': 65},     # D1 to F4
    'guitar': {'min': 40, 'max': 88}    # E2 to E6
}

INST_PITCH_RANGE_EXTENDED_DICT = {
    'violin': {'min': 55, 'max': 105},  # G3 to A7
    'viola': {'min': 48, 'max': 96},    # C3 to C7
    'cello': {'min': 36, 'max': 88},    # C2 to E6
    'double_bass': {'min': 24, 'max': 71},  # C1 to B4
    'flute': {'min': 59, 'max': 101},   # B3 to F7
    'oboe': {'min': 57, 'max': 96},     # A3 to C7
    'clarinet': {'min': 50, 'max': 94}, # D3 to Bb6
    'saxophone': {'min': 46, 'max': 85},  # Bb2 to Db6 (알토 색소폰 기준)
    'bassoon': {'min': 34, 'max': 79},  # Bb1 to G5
    'trumpet': {'min': 52, 'max': 89},  # E3 to F6
    'horn': {'min': 35, 'max': 79},     # B1 to G5
    'trombone': {'min': 40, 'max': 86}, # E2 to D6
    'tuba': {'min': 24, 'max': 67},     # C1 to G4
    'guitar': {'min': 40, 'max': 95}    # E2 to B6
}

def get_pitch_range_from_midi_file(midi_file_path):
    midi_data = pretty_midi.PrettyMIDI(midi_file_path)
    all_pitches = []
    
    for instrument in midi_data.instruments:
        if instrument.is_drum:
            continue
        for note in instrument.notes:
            all_pitches.append(note.pitch)
            
    if not all_pitches:
        return None
        
    pitch_range = {
        'min': min(all_pitches),
        'max': max(all_pitches),
        'mean': sum(all_pitches) / len(all_pitches),
        'median': sorted(all_pitches)[len(all_pitches)//2]
    }
    
    return pitch_range

def get_optimal_pitch_shift(midi_file, instrument):
  # Get pitch range from MIDI file
  midi_pitch_range = get_pitch_range_from_midi_file(midi_file)
  if midi_pitch_range is None:
    return 0
    
  # Get target instrument's pitch range
  target_range = INST_PITCH_RANGE_DICT[instrument]
  print("--------------------------------")
  print(f"Shifting the pitch of the MIDI file to {instrument}'s pitch range")
  print("--------------------------------")
  # Use median instead of min/max to avoid outliers
  midi_center = midi_pitch_range['median']
  print(f"The median of the MIDI file is: {midi_center}")
  print(f"The target instrument({instrument})'s pitch range is: {target_range}")
  target_center = (target_range['max'] + target_range['min']) / 2
  print(f"The center of the target instrument's pitch range is: {target_center}")
  # Calculate initial offset to align centers
  pitch_offset = target_center - midi_center
  print(f"The initial offset to align centers is: {pitch_offset}")
  
  # Round to nearest octave
  octaves = round(pitch_offset / 12)
  pitch_offset = octaves * 12
  print(f"The rounded offset to nearest octave is: {pitch_offset}")
  # Check if we need to shift up/down one more octave
  shifted_median = midi_pitch_range['median'] + pitch_offset
  print(f"The shifted median is: {shifted_median}")
  # If median is closer to the edge of target range, try shifting one octave
  dist_to_min = abs(shifted_median - target_range['min'])
  dist_to_max = abs(shifted_median - target_range['max'])
  print(f"The distance to the minimum of the target range is: {dist_to_min}")
  print(f"The distance to the maximum of the target range is: {dist_to_max}")
  if dist_to_min < dist_to_max * 0.5 and shifted_median + 12 <= target_range['max']:
    pitch_offset += 12
  elif dist_to_max < dist_to_min * 0.5 and shifted_median - 12 >= target_range['min']:
    pitch_offset -= 12
  print(f"The final pitch offset is: {pitch_offset}")
  print("--------------------------------")
  return int(pitch_offset)

