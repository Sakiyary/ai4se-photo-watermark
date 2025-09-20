"""Integration tests using real image files."""

import tempfile
from pathlib import Path

import pytest

from photo_watermark.core.image_processor import ImageProcessor
from photo_watermark.core.watermark import WatermarkConfig, WatermarkPosition


class TestIntegration:
    """Integration tests with real image files."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.processor = ImageProcessor()
        self.fixtures_dir = Path(__file__).parent / "fixtures"
        self.config = WatermarkConfig(
            font_size=24,
            color="white",
            position=WatermarkPosition.BOTTOM_RIGHT,
            margin=10
        )
    
    def test_fixtures_exist(self):
        """Test that fixture files exist."""
        assert self.fixtures_dir.exists()
        
        # List available test files
        test_files = list(self.fixtures_dir.glob("*.jpg"))
        test_files.extend(self.fixtures_dir.glob("*.jpeg"))
        test_files.extend(self.fixtures_dir.glob("*.tiff"))
        test_files.extend(self.fixtures_dir.glob("*.tif"))
        
        print(f"Found test image files: {[f.name for f in test_files]}")
        assert len(test_files) > 0, "No test image files found in fixtures directory"
    
    def test_exif_reading_real_images(self):
        """Test EXIF reading on real image files."""
        test_files = list(self.fixtures_dir.glob("*.jpg"))
        test_files.extend(self.fixtures_dir.glob("*.jpeg"))
        
        if not test_files:
            pytest.skip("No JPEG test files available")
        
        for image_file in test_files:
            print(f"Testing EXIF reading for: {image_file.name}")
            
            # Test EXIF extraction
            date_result = self.processor.exif_reader.get_formatted_date(image_file)
            
            if date_result:
                print(f"  Found EXIF date: {date_result}")
                # Verify date format
                assert len(date_result) == 10  # YYYY-MM-DD
                assert date_result[4] == '-'
                assert date_result[7] == '-'
            else:
                print(f"  No EXIF date found (this is okay)")
    
    def test_image_info_real_images(self):
        """Test getting image info for real images."""
        test_files = list(self.fixtures_dir.glob("*.jpg"))
        test_files.extend(self.fixtures_dir.glob("*.jpeg"))
        
        if not test_files:
            pytest.skip("No test files available")
        
        for image_file in test_files:
            print(f"Getting info for: {image_file.name}")
            
            info = self.processor.get_image_info(image_file)
            
            print(f"  Supported: {info['supported']}")
            if info['supported']:
                print(f"  Size: {info['size']}")
                print(f"  Mode: {info['mode']}")
                print(f"  Format: {info['format']}")
                print(f"  File size: {info['file_size']} bytes")
                print(f"  Has EXIF date: {info['has_exif_date']}")
                if info['exif_date']:
                    print(f"  EXIF date: {info['exif_date']}")
                
                assert info['size'] is not None
                assert len(info['size']) == 2
                assert info['mode'] in ['RGB', 'RGBA', 'L', 'CMYK']
                assert info['file_size'] > 0
    
    def test_watermark_application_real_image(self):
        """Test watermark application on a real image."""
        # Find a JPEG test file
        test_files = list(self.fixtures_dir.glob("*.jpg"))
        if not test_files:
            test_files = list(self.fixtures_dir.glob("*.jpeg"))
        
        if not test_files:
            pytest.skip("No JPEG test files available")
        
        test_file = test_files[0]
        print(f"Testing watermark application on: {test_file.name}")
        
        # Create temporary output directory
        temp_dir = Path(tempfile.mkdtemp())
        output_file = temp_dir / f"watermarked_{test_file.name}"
        
        try:
            # Load image
            image = self.processor.load_image(test_file)
            print(f"  Loaded image: {image.size} {image.mode}")
            
            # Get EXIF date or use a default
            date_text = self.processor.exif_reader.get_formatted_date(test_file)
            if not date_text:
                date_text = "2024-03-15"  # Default for testing
            print(f"  Using date text: {date_text}")
            
            # Apply watermark
            watermarked = self.processor.add_watermark(image, date_text, self.config)
            print(f"  Applied watermark")
            
            # Save result
            self.processor.save_image(watermarked, output_file)
            print(f"  Saved to: {output_file}")
            
            # Verify output file was created
            assert output_file.exists()
            assert output_file.stat().st_size > 0
            
            # Verify we can load the output image
            result_image = self.processor.load_image(output_file)
            assert result_image.size == image.size
            assert result_image.mode == image.mode
            
            print("  ✓ Watermark application successful!")
            
        finally:
            # Cleanup
            if output_file.exists():
                output_file.unlink()
            if temp_dir.exists():
                temp_dir.rmdir()
    
    def test_directory_processing_real_images(self):
        """Test directory processing with real images."""
        # Create a temporary test directory with copies of test images
        temp_input_dir = Path(tempfile.mkdtemp())
        
        try:
            # Copy some test images to temp directory
            test_files = list(self.fixtures_dir.glob("*.jpg"))[:2]  # Limit to 2 files
            
            if not test_files:
                pytest.skip("No JPEG test files available")
            
            # Copy test files to temp directory
            for i, test_file in enumerate(test_files):
                from shutil import copy2
                dest_file = temp_input_dir / f"test_image_{i+1}.jpg"
                copy2(test_file, dest_file)
            
            print(f"Processing directory: {temp_input_dir}")
            print(f"Input files: {[f.name for f in temp_input_dir.glob('*.jpg')]}")
            
            # Process directory
            progress_calls = []
            def progress_callback(current, total, filename, success):
                progress_calls.append((current, total, filename, success))
                print(f"  Progress: {current}/{total} - {filename} - {'✓' if success else '✗'}")
            
            processed, total = self.processor.process_directory(
                temp_input_dir,
                self.config,
                progress_callback=progress_callback
            )
            
            print(f"Processing result: {processed}/{total}")
            
            # Check output directory was created
            output_dir = temp_input_dir.parent / f"{temp_input_dir.name}_watermark"
            assert output_dir.exists()
            
            # Check output files
            output_files = list(output_dir.glob("*.jpg"))
            print(f"Output files: {[f.name for f in output_files]}")
            
            # We should have some results (may not be all if no EXIF dates)
            assert len(output_files) <= len(test_files)
            assert processed <= total
            assert len(progress_calls) == total
            
            # Verify output files are valid
            for output_file in output_files:
                assert output_file.stat().st_size > 0
                # Quick verification that it's a valid image
                result_image = self.processor.load_image(output_file)
                assert result_image.size is not None
            
            print("  ✓ Directory processing successful!")
            
        finally:
            # Cleanup
            import shutil
            if temp_input_dir.exists():
                shutil.rmtree(temp_input_dir)
            
            output_dir = temp_input_dir.parent / f"{temp_input_dir.name}_watermark"
            if output_dir.exists():
                shutil.rmtree(output_dir)
    
    def test_cli_integration_real_image(self):
        """Test CLI integration with real image."""
        from click.testing import CliRunner
        from photo_watermark.cli import main
        
        # Find a test image
        test_files = list(self.fixtures_dir.glob("*.jpg"))
        if not test_files:
            pytest.skip("No JPEG test files available")
        
        test_file = test_files[0]
        
        # Create temporary output
        temp_dir = Path(tempfile.mkdtemp())
        output_file = temp_dir / f"cli_test_{test_file.name}"
        
        try:
            runner = CliRunner()
            
            # Test CLI command
            result = runner.invoke(main, [
                str(test_file),
                '--output', str(output_file),
                '--font-size', '20',
                '--color', 'yellow',
                '--position', 'top-left',
                '--verbose'
            ])
            
            print(f"CLI exit code: {result.exit_code}")
            print(f"CLI output:\n{result.output}")
            
            # Check if processing was successful based on available EXIF data
            if result.exit_code == 0:
                assert output_file.exists()
                assert output_file.stat().st_size > 0
                print("  ✓ CLI integration successful!")
            else:
                # May fail if no EXIF date - check the error message
                assert "No EXIF date found" in result.output or "No images were processed" in result.output
                print("  ⚠ CLI skipped image (no EXIF date) - this is expected behavior")
            
        finally:
            # Cleanup
            if output_file.exists():
                output_file.unlink()
            if temp_dir.exists():
                temp_dir.rmdir()
    
    def test_different_watermark_positions(self):
        """Test different watermark positions on real image."""
        test_files = list(self.fixtures_dir.glob("*.jpg"))
        if not test_files:
            pytest.skip("No JPEG test files available")
        
        test_file = test_files[0]
        temp_dir = Path(tempfile.mkdtemp())
        
        positions = [
            WatermarkPosition.TOP_LEFT,
            WatermarkPosition.TOP_RIGHT,
            WatermarkPosition.CENTER,
            WatermarkPosition.BOTTOM_LEFT,
            WatermarkPosition.BOTTOM_RIGHT
        ]
        
        try:
            image = self.processor.load_image(test_file)
            date_text = "2024-03-15"  # Use fixed date for testing
            
            for position in positions:
                config = WatermarkConfig(
                    font_size=20,
                    color="red",
                    position=position,
                    margin=15
                )
                
                output_file = temp_dir / f"watermark_{position.value}.jpg"
                
                # Apply watermark
                watermarked = self.processor.add_watermark(image, date_text, config)
                self.processor.save_image(watermarked, output_file)
                
                # Verify file was created
                assert output_file.exists()
                assert output_file.stat().st_size > 0
                
                print(f"  ✓ Position {position.value} applied successfully")
            
        finally:
            # Cleanup
            import shutil
            if temp_dir.exists():
                shutil.rmtree(temp_dir)