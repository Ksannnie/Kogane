import AVFoundation
import AudioToolbox
import CoreAudio
import Foundation
import Speech

func fail(
    _ stage: String,
    reason: String,
    error: Error? = nil,
    details: [String: String] = [:]
) -> Never {
    var fields = ["stage=\(stage)", "reason=\(reason)"]
    if let error = error {
        let details = error as NSError
        let safeDomain = String(details.domain.unicodeScalars.filter {
            CharacterSet.alphanumerics.union(CharacterSet(charactersIn: "._-")).contains($0)
        }.prefix(80))
        fields.append("domain=\(safeDomain)")
        fields.append("code=\(details.code)")
    }
    fields.append(contentsOf: details.sorted { $0.key < $1.key }.map { "\($0.key)=\($0.value)" })
    fputs("KOGANE_DIAGNOSTIC \(fields.joined(separator: " "))\n", stderr)
    exit(1)
}

func inputDeviceDetails(for inputNode: AVAudioInputNode) -> (name: String, id: String) {
    guard let audioUnit = inputNode.audioUnit else { return ("unknown", "unknown") }
    var deviceID = AudioDeviceID()
    var deviceIDSize = UInt32(MemoryLayout<AudioDeviceID>.size)
    let deviceStatus = AudioUnitGetProperty(
        audioUnit,
        kAudioOutputUnitProperty_CurrentDevice,
        kAudioUnitScope_Global,
        0,
        &deviceID,
        &deviceIDSize
    )
    guard deviceStatus == noErr else { return ("unknown", "unknown") }

    var address = AudioObjectPropertyAddress(
        mSelector: kAudioObjectPropertyName,
        mScope: kAudioObjectPropertyScopeGlobal,
        mElement: kAudioObjectPropertyElementMain
    )
    var name: CFString? = nil
    var nameSize = UInt32(MemoryLayout<CFString?>.size)
    let nameStatus = withUnsafeMutableBytes(of: &name) { bytes in
        AudioObjectGetPropertyData(deviceID, &address, 0, nil, &nameSize, bytes.baseAddress!)
    }
    guard nameStatus == noErr else { return ("unknown", String(deviceID)) }

    guard let name else { return ("unknown", String(deviceID)) }
    let safeName = String(name).unicodeScalars.map { scalar -> Character in
        CharacterSet.alphanumerics.union(CharacterSet(charactersIn: "._-"))
            .contains(scalar) ? Character(scalar) : "_"
    }
    return (String(safeName.prefix(80)), String(deviceID))
}

final class CaptureDiagnostics {
    private let lock = NSLock()
    private var bufferCount = 0
    private var sampleCount = 0
    private var sumSquares = 0.0
    private var peak = 0.0
    private var partialResultCount = 0
    private var nonemptyPartialCount = 0
    private var longestPartialCharacterCount = 0
    private var finalTranscriptCharacterCount = 0
    private var finalResultReceived = false
    private var validTranscriptOverwritten = false
    private var endAudioCalled = false
    private var taskState = "created"
    private var transcript = ""
    private var finalTranscript = ""
    private var partialTranscript = ""
    private var transcriptSource = "none"
    private var recognitionError: NSError?

    func record(_ buffer: AVAudioPCMBuffer) {
        var currentPeak = 0.0
        var currentSumSquares = 0.0
        var currentSampleCount = 0
        let frames = Int(buffer.frameLength)
        switch buffer.format.commonFormat {
        case .pcmFormatFloat32:
            if let channels = buffer.floatChannelData {
                for channel in 0..<Int(buffer.format.channelCount) {
                    for frame in 0..<frames {
                        let sample = Double(channels[channel][frame])
                        currentPeak = max(currentPeak, abs(sample))
                        currentSumSquares += sample * sample
                        currentSampleCount += 1
                    }
                }
            }
        case .pcmFormatInt16:
            if let channels = buffer.int16ChannelData {
                for channel in 0..<Int(buffer.format.channelCount) {
                    for frame in 0..<frames {
                        let sample = Double(channels[channel][frame]) / Double(Int16.max)
                        currentPeak = max(currentPeak, abs(sample))
                        currentSumSquares += sample * sample
                        currentSampleCount += 1
                    }
                }
            }
        case .pcmFormatInt32:
            if let channels = buffer.int32ChannelData {
                for channel in 0..<Int(buffer.format.channelCount) {
                    for frame in 0..<frames {
                        let sample = Double(channels[channel][frame]) / Double(Int32.max)
                        currentPeak = max(currentPeak, abs(sample))
                        currentSumSquares += sample * sample
                        currentSampleCount += 1
                    }
                }
            }
        default:
            break
        }

        lock.lock()
        bufferCount += 1
        sampleCount += currentSampleCount
        sumSquares += currentSumSquares
        peak = max(peak, currentPeak)
        lock.unlock()
    }

    func setTaskState(_ state: String) {
        lock.lock()
        taskState = state
        lock.unlock()
    }

    func recordPartialResult(_ value: String) {
        let candidate = value.trimmingCharacters(in: .whitespacesAndNewlines)
        lock.lock()
        partialResultCount += 1
        if !candidate.isEmpty {
            nonemptyPartialCount += 1
            if candidate.count >= longestPartialCharacterCount {
                longestPartialCharacterCount = candidate.count
                partialTranscript = candidate
            }
        }
        taskState = "partial_result"
        lock.unlock()
    }

    func recordFinalResult(_ value: String) {
        let finalValue = value.trimmingCharacters(in: .whitespacesAndNewlines)
        lock.lock()
        finalTranscriptCharacterCount = finalValue.count
        if !finalValue.isEmpty {
            finalTranscript = finalValue
            transcript = finalValue
            transcriptSource = "final"
        } else if !partialTranscript.isEmpty {
            transcript = partialTranscript
            transcriptSource = "partial"
            validTranscriptOverwritten = true
        }
        finalResultReceived = true
        taskState = "final_result"
        lock.unlock()
    }

    func recordError(_ error: Error) {
        lock.lock()
        recognitionError = error as NSError
        taskState = "error"
        lock.unlock()
    }

    func markEndAudio() {
        lock.lock()
        endAudioCalled = true
        taskState = "awaiting_result"
        lock.unlock()
    }

    func transcriptValue() -> String {
        lock.lock()
        defer { lock.unlock() }
        return transcript
    }

    func transcriptCandidates() -> (final: String, partial: String) {
        lock.lock()
        defer { lock.unlock() }
        return (finalTranscript, partialTranscript)
    }

    func errorValue() -> NSError? {
        lock.lock()
        defer { lock.unlock() }
        return recognitionError
    }

    func fields() -> [String: String] {
        lock.lock()
        defer { lock.unlock() }
        let rms = sampleCount == 0 ? 0 : sqrt(sumSquares / Double(sampleCount))
        var values = [
            "buffers": String(bufferCount),
            "level_samples": String(sampleCount),
            "rms": String(format: "%.6f", rms),
            "peak": String(format: "%.6f", peak),
            "partial_results": String(partialResultCount),
            "nonempty_partial_results": String(nonemptyPartialCount),
            "longest_partial_characters": String(longestPartialCharacterCount),
            "final_transcript_characters": String(finalTranscriptCharacterCount),
            "valid_transcript_overwritten": validTranscriptOverwritten ? "yes" : "no",
            "transcript_source": transcriptSource,
            "final_result": finalResultReceived ? "yes" : "no",
            "end_audio": endAudioCalled ? "yes" : "no",
            "task_state": taskState,
        ]
        if let error = recognitionError {
            values["error_domain"] = String(error.domain.unicodeScalars.filter {
                CharacterSet.alphanumerics.union(CharacterSet(charactersIn: "._-"))
                    .contains($0)
            }.prefix(80))
            values["error_code"] = String(error.code)
        }
        return values
    }
}

for key in ["NSMicrophoneUsageDescription", "NSSpeechRecognitionUsageDescription"] {
    guard let value = Bundle.main.object(forInfoDictionaryKey: key) as? String,
          !value.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else {
        fail("configuration", reason: "USAGE_DESCRIPTION_MISSING")
    }
}

let microphonePermission = AVCaptureDevice.authorizationStatus(for: .audio)
if microphonePermission == .notDetermined {
    let permissionGate = DispatchSemaphore(value: 0)
    var microphoneGranted = false
    AVCaptureDevice.requestAccess(for: .audio) { granted in
        microphoneGranted = granted
        permissionGate.signal()
    }
    guard permissionGate.wait(timeout: .now() + 15) == .success else {
        fail("microphone_authorization", reason: "AUTHORIZATION_TIMEOUT")
    }
    if !microphoneGranted {
        fail("microphone_authorization", reason: "MIC_PERMISSION_DENIED")
    }
} else if microphonePermission != .authorized {
    fail("microphone_authorization", reason: "MIC_PERMISSION_DENIED")
}

let speechPermissionGate = DispatchSemaphore(value: 0)
var speechPermission = SFSpeechRecognizer.authorizationStatus()
if speechPermission == .notDetermined {
    SFSpeechRecognizer.requestAuthorization { status in
        speechPermission = status
        speechPermissionGate.signal()
    }
    guard speechPermissionGate.wait(timeout: .now() + 15) == .success else {
        fail("speech_authorization", reason: "AUTHORIZATION_TIMEOUT")
    }
} else if speechPermission == .authorized {
    speechPermission = .authorized
}
if speechPermission != .authorized {
    fail("speech_authorization", reason: "SPEECH_PERMISSION_DENIED")
}

guard let recognizer = SFSpeechRecognizer(locale: Locale(identifier: "en-US")) else {
    fail("recognizer", reason: "RECOGNIZER_UNAVAILABLE")
}
guard recognizer.isAvailable else {
    fail("recognizer", reason: "RECOGNIZER_UNAVAILABLE", details: [
        "recognizer_available": "no",
        "on_device_supported": String(recognizer.supportsOnDeviceRecognition),
    ])
}
guard recognizer.supportsOnDeviceRecognition else {
    fail("recognizer", reason: "NO_LOCAL_RECOGNIZER", details: [
        "recognizer_available": "yes",
        "on_device_supported": "no",
    ])
}

let audioEngine = AVAudioEngine()
let inputNode = audioEngine.inputNode
let audioFormat = inputNode.inputFormat(forBus: 0)
let device = inputDeviceDetails(for: inputNode)
let inputDetails = [
    "device": device.name,
    "device_id": device.id,
    "sample_rate": String(format: "%.1f", audioFormat.sampleRate),
    "channels": String(audioFormat.channelCount),
    "format": String(describing: audioFormat.commonFormat),
    "engine_started": "no",
    "recognizer_available": "yes",
    "on_device_supported": "yes",
]
guard audioFormat.channelCount > 0 else {
    fail("audio_input", reason: "NO_MICROPHONE", details: inputDetails)
}

let capture = CaptureDiagnostics()
let request = SFSpeechAudioBufferRecognitionRequest()
request.requiresOnDeviceRecognition = true
request.shouldReportPartialResults = true
let completionGate = DispatchSemaphore(value: 0)
let recognitionCallbackQueue = OperationQueue()
recognitionCallbackQueue.name = "com.kogane.speech-input.recognition-callbacks"
recognitionCallbackQueue.qualityOfService = .userInitiated
recognitionCallbackQueue.maxConcurrentOperationCount = 1
recognizer.queue = recognitionCallbackQueue

let recognitionTask = recognizer.recognitionTask(with: request) { result, error in
    if let result = result {
        if result.isFinal {
            capture.recordFinalResult(result.bestTranscription.formattedString)
            completionGate.signal()
        } else {
            capture.recordPartialResult(result.bestTranscription.formattedString)
        }
    }
    if let error = error {
        capture.recordError(error)
        completionGate.signal()
    }
}
capture.setTaskState("running")

inputNode.installTap(onBus: 0, bufferSize: 1024, format: audioFormat) { buffer, _ in
    capture.record(buffer)
    request.append(buffer)
}

do {
    try audioEngine.start()
} catch {
    inputNode.removeTap(onBus: 0)
    recognitionTask.cancel()
    fail("audio_engine_start", reason: "AUDIO_ERROR", error: error, details: inputDetails)
}
var captureDetails = inputDetails
captureDetails["engine_started"] = audioEngine.isRunning ? "yes" : "no"
fputs("KOGANE_READY\n", stderr)

_ = DispatchSemaphore(value: 0).wait(timeout: .now() + .seconds(6))
audioEngine.stop()
inputNode.removeTap(onBus: 0)
request.endAudio()
capture.markEndAudio()

if completionGate.wait(timeout: .now() + .seconds(10)) != .success {
    capture.setTaskState("recognition_timeout")
    recognitionTask.cancel()
    var details = capture.fields()
    details.merge(captureDetails) { _, newValue in newValue }
    if details["buffers"] == "0" {
        fail("audio_capture", reason: "NO_AUDIO_BUFFERS", details: details)
    }
    if details["level_samples"] != "0", details["peak"] == "0.000000" {
        fail("audio_capture", reason: "SILENT_AUDIO", details: details)
    }
    fail("recognition_timeout", reason: "RECOGNITION_TIMEOUT", details: details)
}

if let error = capture.errorValue() {
    var details = capture.fields()
    details.merge(captureDetails) { _, newValue in newValue }
    fail("recognition", reason: "SPEECH_ERROR", error: error, details: details)
}
let cleanedTranscript = capture.transcriptValue().trimmingCharacters(in: .whitespacesAndNewlines)
if cleanedTranscript.isEmpty {
    var details = capture.fields()
    details.merge(captureDetails) { _, newValue in newValue }
    fail("transcription", reason: "EMPTY_TRANSCRIPTION", details: details)
}
fputs("KOGANE_DIAGNOSTIC status=ok \(capture.fields().map { "\($0.key)=\($0.value)" }.sorted().joined(separator: " "))\n", stderr)
let candidates = capture.transcriptCandidates()
let output: [String: String] = [
    "final_transcript": candidates.final,
    "partial_transcript": candidates.partial,
]
let outputData = try JSONSerialization.data(withJSONObject: output, options: [.sortedKeys])
guard let outputText = String(data: outputData, encoding: .utf8) else {
    fail("transcription_output", reason: "OUTPUT_ENCODING_FAILED")
}
print(outputText)
