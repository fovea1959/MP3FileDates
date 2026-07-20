import struct
import discid
from mutagen import File


def calculate_disc_id_from_mcdi(file_path):
    # 1. Extract raw binary MCDI data using mutagen
    audio_file = File(file_path)
    if not audio_file or 'MCDI' not in audio_file:
        raise ValueError("No MCDI tag found in this file.")

    mcdi_data = audio_file['MCDI'].data

    # 2. Extract track information from the 4-byte header
    # Byte 2 = First Track, Byte 3 = Last Track
    first_track = mcdi_data[2]
    last_track = mcdi_data[3]
    total_tracks = (last_track - first_track) + 1

    offsets = []
    leadout_offset = 0

    # 3. Step through the 8-byte track blocks
    # The header takes the first 4 bytes.
    pointer = 4

    # Loop over total tracks + 1 to account for the Lead-Out track entry
    for i in range(total_tracks + 1):
        # Extract the 8-byte block for this track descriptor
        track_block = mcdi_data[pointer: pointer + 8]

        # Byte 2 of the track block specifies the track number (or 0xAA / 170 for lead-out)
        track_num = track_block[2]

        # The last 4 bytes of the 8-byte block contain the big-endian LBA frame address
        lba_offset = struct.unpack('>I', track_block[4:8])[0]

        if track_num == 0xAA or i == total_tracks:
            leadout_offset = lba_offset
        else:
            offsets.append(lba_offset)

        pointer += 8  # Advance to the next 8-byte track entry

    try:
        # 4. Construct the disc ID using python-discid
        disc = discid.put(first_track, last_track, leadout_offset, offsets)

        print(f"MusicBrainz Disc ID: {disc.id}")
        print(f"FreeDB ID: {disc.freedb_id}")
        return disc.id

    except discid.TOCError as e:
        print(f"TOC compilation error: {e}")

# Example Usage:
calculate_disc_id_from_mcdi("mp3/Milt Jackson/Sa Va Bella (For Lady Legends)/01. Oh, Lady Be Good.mp3")
