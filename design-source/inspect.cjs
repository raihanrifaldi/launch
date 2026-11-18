const fs = require('node:fs');
const zlib = require('node:zlib');
const kiwi = require('kiwi-schema');
const fzstd = require('fzstd');
const data = fs.readFileSync(__dirname + '/canvas.fig');
const chunks = [];
for (let offset = 12; offset + 4 < data.length;) {
  const size = data.readUInt32LE(offset);
  chunks.push(data.subarray(offset + 4, offset + 4 + size));
  offset += size + 4;
}
const schema = kiwi.compileSchema(kiwi.decodeBinarySchema(zlib.inflateRawSync(chunks[0])));
const raw = chunks[1].readUInt32LE(0) === 0xfd2fb528 ? fzstd.decompress(chunks[1]) : zlib.inflateRawSync(chunks[1]);
const message = schema.decodeMessage(raw);
fs.writeFileSync(__dirname + '/document.json', JSON.stringify(message));
console.log('Keys:', Object.keys(message), 'Nodes:', message.nodeChanges?.length);
for (const n of message.nodeChanges || []) {
  if (['CANVAS', 'FRAME', 'SECTION'].includes(n.type)) console.log(JSON.stringify({id:n.guid, name:n.name,type:n.type,parent:n.parentIndex,size:n.size, transform:n.transform}));
}
