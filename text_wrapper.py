class TextWrapper:
    """Handles text wrapping for both UI table and image exports"""
    
    @staticmethod
    def wrap_text(text, max_chars):
        """Wrap text to fit within character limit (for UI table display)"""
        if len(text) <= max_chars:
            return text
        
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            if len(current_line) + len(word) + 1 <= max_chars:
                current_line += word + " "
            else:
                if current_line:
                    lines.append(current_line.strip())
                current_line = word + " "
        
        if current_line:
            lines.append(current_line.strip())
        
        return "\n".join(lines) if lines else text
    
    @staticmethod
    def wrap_text_for_image(text, max_char_width, col_width, draw, font):
        """Wrap text to fit within pixel width (for image exports)"""
        if not text:
            return []
        
        lines = []
        words = text.split()
        current_line = ""
        
        for word in words:
            test_line = current_line + word + " "
            bbox = draw.textbbox((0, 0), test_line, font=font)
            line_width = bbox[2] - bbox[0]
            
            if line_width <= col_width - 20:  # Leave padding for cell margins
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line.strip())
                current_line = word + " "
        
        if current_line:
            lines.append(current_line.strip())
        
        return lines
    
    @staticmethod
    def get_line_height(draw, font):
        """Get the height of a single line of text"""
        bbox = draw.textbbox((0, 0), "Agy", font=font)
        return bbox[3] - bbox[1] + 5  # Add small spacing
