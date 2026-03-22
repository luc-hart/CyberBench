import pyperclip

class AsciiSmuggling:
    ZW0 = "\u200B"  # Zero Width Space (represents bit 0)
    ZW1 = "\u200C"  # Zero Width Non-Joiner (represents bit 1)

    def __init__(self, prompt: str):
        self.prompt = prompt

    def char_to_zw(self, ch: str) -> str:
        """Convert a character into 8 zero-width bits."""
        bits = f"{ord(ch):08b}"  # 8-bit binary representation
        return ''.join(self.ZW1 if b == '1' else self.ZW0 for b in bits)

    def convert_to_zero_width(self):
        """Convert the entire prompt into zero-width smuggled text."""
        return ''.join(self.char_to_zw(ch) for ch in self.prompt)

    def run(self):
        return self.convert_to_zero_width()


# Example usage
if __name__ == "__main__":
    prompt = "test prompt."
    attack = AsciiSmuggling(prompt)
    tagged = attack.run()

    with open("zero_width_output.txt", "w", encoding="utf-8") as f:
        f.write(tagged)

    print("Zero-width encoded output written to zero_width_output.txt")
