function decodeUplink(input) {
    var bytes = input.bytes
    return {
      data: {
        distance: ((bytes[0] & 0x80 ? 0xFFFF<<16 : 0) | bytes[0]<<8 | bytes[1]),
        temperaturec: ((bytes[2] & 0x80 ? 0xFFFF<<16 : 0) | bytes[2]<<8 | bytes[3]),
        voltage : (bytes[4]<<8 | bytes[5])
      },
      warnings: [],
      errors: []
    };
  }