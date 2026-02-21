import os
import subprocess
import platform
from pathlib import Path
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont


class ImageExporter:
    """Handles image generation and export for activities"""
    
    def __init__(self, settings_manager):
        self.settings = settings_manager.settings
    
    def _wrap_text_for_image(self, text, max_char_width, col_width, draw, font):
        """Wrap text to fit within a column width and return list of lines"""
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
    
    def _get_line_height(self, draw, font):
        """Get the height of a single line of text"""
        bbox = draw.textbbox((0, 0), "Agy", font=font)
        return bbox[3] - bbox[1] + 5  # Add small spacing
    
    def generate_preview_image(self, settings_dict, activities=None):
        """Generate a preview image with given settings and optional activities"""
        padding = settings_dict["padding"]
        cell_padding = settings_dict["cell_padding"]
        min_row_height = settings_dict["min_row_height"]
        col_widths = settings_dict["column_widths"]
        
        header_bg = (44, 62, 80)
        header_fg = (255, 255, 255)
        row_bg = (255, 255, 255)
        border_color = (220, 220, 220)
        text_color = (51, 51, 51)
        title_color = (51, 51, 51)
        
        try:
            title_font = ImageFont.truetype("arial.ttf", settings_dict["title_font_size"])
            header_font = ImageFont.truetype("arial.ttf", settings_dict["header_font_size"])
            body_font = ImageFont.truetype("arial.ttf", settings_dict["body_font_size"])
        except:
            title_font = header_font = body_font = ImageFont.load_default()
        
        # Use actual activities if provided, otherwise use sample data
        if activities is None:
            activities = [
                {"proyecto_area": "Website Redesign", "avance": "60% Complete", "impacto": "High Priority", "estado": "en progreso"},
                {"proyecto_area": "Database Migration", "avance": "Testing Phase", "impacto": "Critical", "estado": "en progreso"},
            ]
        else:
            # Limit to first 10 activities for preview
            activities = activities[:10]
        
        temp_img = Image.new("RGB", (1, 1))
        temp_draw = ImageDraw.Draw(temp_img)
        line_height = self._get_line_height(temp_draw, body_font)
        
        # Calculate row heights with text wrapping
        row_heights = []
        wrapped_content = []
        
        for activity in activities:
            proyecto_lines = self._wrap_text_for_image(activity.get("proyecto_area", ""), None, col_widths[0], temp_draw, body_font)
            avance_lines = self._wrap_text_for_image(activity.get("avance", ""), None, col_widths[1], temp_draw, body_font)
            impacto_lines = self._wrap_text_for_image(activity.get("impacto", ""), None, col_widths[2], temp_draw, body_font)
            estado_lines = [activity.get("estado", "pendiente")]
            
            max_lines = max(len(proyecto_lines), len(avance_lines), len(impacto_lines), len(estado_lines))
            row_height = max(min_row_height, (max_lines * line_height) + (cell_padding * 2))
            
            row_heights.append(row_height)
            wrapped_content.append({
                'proyecto': proyecto_lines,
                'avance': avance_lines,
                'impacto': impacto_lines,
                'estado': estado_lines
            })
        
        # Calculate dimensions
        title_height = 60
        header_height = 50
        content_height = sum(row_heights)
        summary_height = 40
        total_height = title_height + header_height + content_height + summary_height + (padding * 2)
        total_width = sum(col_widths) + (padding * 2) + 2
        
        # Create image
        img = Image.new("RGB", (total_width, total_height), (255, 255, 255))
        draw = ImageDraw.Draw(img)
        
        y = padding
        
        # Draw title
        draw.text((padding + 10, y), "Daily Logbook - Preview", fill=title_color, font=title_font)
        y += title_height
        
        # Draw header
        x = padding
        headers = ["Proyecto/Area", "Avance", "Impacto", "Estado"]
        draw.rectangle(
            [(padding, y), (total_width - padding, y + header_height)],
            fill=header_bg, outline=border_color
        )
        
        for i, header in enumerate(headers):
            draw.text((x + cell_padding, y + cell_padding), header, fill=header_fg, font=header_font)
            x += col_widths[i]
        
        y += header_height
        
        # Draw data rows
        for idx, activity in enumerate(activities):
            row_height = row_heights[idx]
            bg_color = row_bg
            draw.rectangle(
                [(padding, y), (total_width - padding, y + row_height)],
                fill=bg_color, outline=border_color
            )
            
            content = wrapped_content[idx]
            x = padding
            
            # Draw each cell with wrapped text
            for col_idx, (lines, col_width) in enumerate(zip(
                [content['proyecto'], content['avance'], content['impacto'], content['estado']],
                col_widths
            )):
                text_y = y + cell_padding
                for line in lines:
                    draw.text((x + cell_padding, text_y), line, fill=text_color, font=body_font)
                    text_y += line_height
                
                x += col_width
            
            y += row_height
        
        # Resize for display (max 800x600 for dialog)
        max_width = 800
        max_height = 600
        if total_width > max_width or total_height > max_height:
            scale = min(max_width / total_width, max_height / total_height)
            new_size = (int(total_width * scale), int(total_height * scale))
            img = img.resize(new_size, Image.Resampling.LANCZOS)
        
        return img
    
    def create_table_image(self, date_str, activities):
        """Create a table image from activities"""
        padding = self.settings["padding"]
        cell_padding = self.settings["cell_padding"]
        min_row_height = self.settings["min_row_height"]
        col_widths = self.settings["column_widths"]
        
        header_bg = (44, 62, 80)  
        header_fg = (255, 255, 255) 
        row_bg_odd = (255, 255, 255)
        row_bg_even = (249, 249, 249)  
        border_color = (220, 220, 220)  
        text_color = (51, 51, 51) 
        title_color = (51, 51, 51)
        
        try:
            title_font = ImageFont.truetype("arial.ttf", self.settings["title_font_size"])
            header_font = ImageFont.truetype("arial.ttf", self.settings["header_font_size"])
            body_font = ImageFont.truetype("arial.ttf", self.settings["body_font_size"])
            summary_font = ImageFont.truetype("arial.ttf", self.settings["summary_font_size"])
        except:
            title_font = header_font = body_font = summary_font = ImageFont.load_default()
        
        temp_img = Image.new("RGB", (1, 1))
        temp_draw = ImageDraw.Draw(temp_img)
        
        # Calculate actual row heights based on wrapped content
        row_heights = []
        wrapped_content = []
        line_height = self._get_line_height(temp_draw, body_font)
        
        for activity in activities:
            proyecto_lines = self._wrap_text_for_image(activity.get("proyecto_area", ""), 25, col_widths[0], temp_draw, body_font)
            avance_lines = self._wrap_text_for_image(activity.get("avance", ""), 20, col_widths[1], temp_draw, body_font)
            impacto_lines = self._wrap_text_for_image(activity.get("impacto", ""), 20, col_widths[2], temp_draw, body_font)
            estado_lines = [activity.get("estado", "pendiente")]
            
            max_lines = max(len(proyecto_lines), len(avance_lines), len(impacto_lines), len(estado_lines))
            row_height = max(min_row_height, (max_lines * line_height) + (cell_padding * 2))
            
            row_heights.append(row_height)
            wrapped_content.append({
                'proyecto': proyecto_lines,
                'avance': avance_lines,
                'impacto': impacto_lines,
                'estado': estado_lines
            })
        
        # Calculate dimensions
        title_height = 80
        header_height = 70
        content_height = sum(row_heights)
        summary_height = 60
        total_height = title_height + header_height + content_height + summary_height + (padding * 2)
        total_width = sum(col_widths) + (padding * 2) + 2 
        
        # Create image
        img = Image.new("RGB", (total_width, total_height), (255, 255, 255))
        draw = ImageDraw.Draw(img)
        
        y = padding
        
        # Draw title
        draw.text((padding + 10, y), f"Daily Logbook - {date_str}", fill=title_color, font=title_font)
        y += title_height
        
        # Draw header
        x = padding
        headers = ["Proyecto/Area", "Avance", "Impacto", "Estado"]
        draw.rectangle(
            [(padding, y), (total_width - padding, y + header_height)],
            fill=header_bg, outline=border_color
        )
        
        for i, header in enumerate(headers):
            draw.text((x + cell_padding, y + cell_padding), header, fill=header_fg, font=header_font)
            x += col_widths[i]
        
        y += header_height
        
        # Draw data rows
        for idx, (activity, row_height) in enumerate(zip(activities, row_heights)):
            bg_color = row_bg_even if idx % 2 == 0 else row_bg_odd
            draw.rectangle(
                [(padding, y), (total_width - padding, y + row_height)],
                fill=bg_color, outline=border_color
            )
            
            content = wrapped_content[idx]
            x = padding
            
            # Draw each cell with wrapped text
            for col_idx, (lines, col_width) in enumerate(zip(
                [content['proyecto'], content['avance'], content['impacto'], content['estado']],
                col_widths
            )):
                text_y = y + cell_padding
                for line in lines:
                    draw.text((x + cell_padding, text_y), line, fill=text_color, font=body_font)
                    text_y += line_height
                
                x += col_width
            
            y += row_height
        
        draw.text((padding + 10, y + 10), f"Total: {len(activities)} activities logged", fill=text_color, font=summary_font)
        
        return img
    
    def copy_image_to_clipboard(self, image):
        """Copy PIL Image to clipboard (cross-platform)"""
        temp_path = Path.home() / ".logbook" / "temp_table.png"
        temp_path.parent.mkdir(exist_ok=True)
        image.save(temp_path, "PNG")
        
        system = platform.system()
        
        try:
            if system == "Windows":
                ps_cmd = f"""
                Add-Type -AssemblyName System.Windows.Forms
                [System.Windows.Forms.Clipboard]::SetImage([System.Drawing.Image]::FromFile('{temp_path}'))
                """
                subprocess.run(["powershell", "-Command", ps_cmd], capture_output=True, check=True)
            
            elif system == "Darwin":
                subprocess.run([
                    "osascript", "-e",
                    f'set the clipboard to (read (POSIX file "{temp_path}") as PNG picture)'
                ], check=True)
            
            elif system == "Linux":
                try:
                    subprocess.run([
                        "xclip", "-selection", "clipboard", "-t", "image/png", "-i", str(temp_path)
                    ], check=True)
                except FileNotFoundError:
                    subprocess.run([
                        "xsel", "--clipboard", "--input"
                    ], stdin=open(temp_path, 'rb'), check=True)
            
            else:
                raise NotImplementedError(f"Clipboard copy not supported on {system}")
        
        except Exception as e:
            desktop = Path.home() / "Desktop" / f"logbook_table_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            image.save(desktop, "PNG")
            raise Exception(f"Clipboard not available. Image saved to: {desktop}")
        
        finally:
            try:
                os.remove(temp_path)
            except:
                pass
