import React, { useState, useEffect, useRef } from 'react';
import { marked } from 'marked';
import DOMPurify from 'dompurify';
import './ChatApp.css';

function ChatApp() {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState([]);
  const websocket = useRef(null);

  // useEffect is a React Hook that allows you to perform side effects in function components.
  // In this case, it's used to establish a WebSocket connection when the component mounts, 
  // and close the connection when the component unmounts.
  useEffect(() => {
    // Create a new WebSocket connection to the specified URL
    websocket.current = new WebSocket('ws://localhost:8765');

    // Set up an event listener for messages received from the server
    websocket.current.onmessage = (event) => {
      // Parse the JSON data from the server
      const data = JSON.parse(event.data);

      // If the data contains an 'answer', append it to the messages array
      if (data.answer) {
        setMessages((prevMessages) => [...prevMessages, `${data.answer}`]);
      }
    };

    // Return a cleanup function to be run when the component unmounts
    return () => {
      // If the WebSocket connection exists, close it
      if (websocket.current) {
        websocket.current.close();
      }
    };
  }, []);  // Empty dependency array means this effect runs once on mount and cleanup on unmount

  /**
   * sendMessage is a function that sends a message through a WebSocket connection.
   * It first checks if the input is not just whitespace, then it sends the input as a JSON string.
   * After sending the message, it appends the message to the messages array and clears the input field.
   */
  const sendMessage = () => {
    // Check if the input is not just whitespace
    if (input.trim()) {
      // Convert the input to a JSON string
      const message = JSON.stringify({ input });

      // Send the message through the WebSocket connection
      websocket.current.send(message);

      // Append the message to the messages array
      setMessages((prevMessages) => [...prevMessages, `You: ${input}`]);

      // Clear the input field after sending the message
      setInput('');  
    }
  };

  /**
   * renderMessageAsMarkdown is a function that takes a message string as input and returns a JSX element.
   * The message is first checked if it's a user message (starts with 'You: ').
   * Depending on whether it's a user message or a server message, it's displayed differently (you on the right, else Nydas on the left).
   * The message is then converted to Markdown using the marked library, and sanitized using DOMPurify to prevent XSS attacks.
   * The function returns a div element with the message displayed as HTML, and different styles and classes depending on whether 
   * it's a user message or a server message.
   */
  const renderMessageAsMarkdown = (msg) => {
    // Check if the message is a user message
    const isUserMessage = msg.startsWith('You: ');

    // Format the display message depending on whether it's a user message or a server message
    const displayMessage = isUserMessage ? `<b>You:</b><br />${msg.substring(5)}` : `<b>Nydas:</b><br />${msg}`;

    // Convert the display message to Markdown
    const rawMarkup = marked(displayMessage);

    // Sanitize the Markdown to prevent XSS attacks
    const sanitizedMarkup = DOMPurify.sanitize(rawMarkup);

    // Return a div element with the message displayed as HTML, and different styles and classes depending on whether it's a user message or a server message
    return (
      <div
        className={isUserMessage ? 'box3 sb13' : 'box3 sb14'}
        key={isUserMessage ? `user-${displayMessage}` : `server-${displayMessage}`}
        style={{
          margin: isUserMessage ? '5px 15px' : '5px 0 5px 15px',
          alignSelf: isUserMessage ? 'flex-end' : 'flex-start'
        }}
        dangerouslySetInnerHTML={{ __html: sanitizedMarkup }}
      />
    );
  };
  /**
   * This is the main render function of the Chatbot component.
   * It returns a JSX element that represents the chat interface.
   * 
   * The chat interface consists of a message display area and an input area.
   * The message display area shows all the messages in reverse order (newest at the top), 
   * and each message is rendered as Markdown using the renderMessageAsMarkdown function.
   * 
   * The input area consists of a text input field and a send button.
   * The text input field updates the input state whenever its value changes, 
   * and it calls the sendMessage function when the Enter key is pressed.
   * The send button also calls the sendMessage function when it's clicked.
   */
  return (
    <div id='background_grad' style={{ height: '100vh', display: 'flex' }}>
      <div style={{ flex: 1, display: 'flex' }}></div>
      <div className="right-section" style={{ flex: '100%', display: 'flex', flexDirection: 'column', margin: '10px', padding: '10px', border: '1px solid #79a0b7' }}>
        <div style={{ overflowY: 'auto', flexGrow: 1, padding: '10px', paddingTop: '120px', display: 'flex', flexDirection: 'column-reverse' }}>
          {[...messages].reverse().map((msg) => renderMessageAsMarkdown(msg))}
        </div>
        <div style={{ display: 'flex', padding: '10px' }}>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
            style={{ flex: 1, marginRight: '10px', padding: '10px' }}
          />
          <button onClick={sendMessage} style={{ padding: '10px' }}>
            Send
          </button>
        </div>
      </div>
    </div>
  );
}

export default ChatApp;