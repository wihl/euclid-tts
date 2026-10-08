// Read the installed macOS voice metadata without changing system settings.
import AVFoundation
import Foundation

var results = [[String: String]]()
for voice in AVSpeechSynthesisVoice.speechVoices() {
    if voice.name == "Melina" {
        let gender = voice.gender == .female ? "female" : voice.gender == .male ? "male" : "unspecified"
        let result = [
            "name": voice.name,
            "gender": gender,
            "locale": voice.language,
            "identifier": voice.identifier,
        ]
        results.append(result)
    }
}
let json = try JSONSerialization.data(withJSONObject: results, options: [.prettyPrinted, .sortedKeys])
print(String(data: json, encoding: .utf8)!)
