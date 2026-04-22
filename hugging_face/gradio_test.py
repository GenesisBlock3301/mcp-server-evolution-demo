import gradio as gr


def letter_counter(word: str, letter: str) -> int:
    """
    Count the number of occurrences of a letter in a word or text.

    Args:
        word (str): The input text to search through
        letter (str): The letter to search for

    Returns:
        int: The number of times the letter appears in the text
    """
    word = word.lower()
    letter = letter.lower()
    count = word.count(letter)
    return count


def text_reverser(text: str) -> str:
    """
    Reverse the characters of any given text.

    Args:
        text (str): The input text to reverse

    Returns:
        str: The reversed version of the input text
    """
    return text[::-1]


letter_counter_ui = gr.Interface(
    fn=letter_counter,
    inputs=["textbox", "textbox"],
    outputs="number",
    title="Letter Counter",
    description="Enter text and a letter to count how many times the letter appears in the text."
)

text_reverser_ui = gr.Interface(
    fn=text_reverser,
    inputs=gr.Textbox(label="Text to Reverse", placeholder="Type anything..."),
    outputs=gr.Textbox(label="Reversed Text"),
    title="Text Reverser",
    description="Enter any text and get it reversed instantly."
)

demo = gr.TabbedInterface(
    [letter_counter_ui, text_reverser_ui],
    tab_names=["Letter Counter", "Text Reverser"]
)

if __name__ == "__main__":
    demo.launch(mcp_server=True)