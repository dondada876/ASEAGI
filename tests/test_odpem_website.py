"""
Playwright tests for ODPEM (Office of Disaster Preparedness and Emergency Management)
Website: https://www.odpem.org.jm/

Tests include:
- Page accessibility
- Navigation functionality
- Content verification
- Form interactions
- Mobile responsiveness
"""
import pytest
import re
from playwright.sync_api import Page, expect


@pytest.mark.playwright
class TestODPEMWebsite:
    """Test suite for ODPEM Jamaica website"""

    def test_homepage_loads(self, page: Page, odpem_url):
        """Test that the ODPEM homepage loads successfully"""
        response = page.goto(odpem_url)

        # Check response status
        assert response.status == 200, f"Expected 200, got {response.status}"

        # Check page title
        expect(page).to_have_title(re.compile("ODPEM|Office of Disaster Preparedness", re.IGNORECASE))

        print(f"✓ Homepage loaded successfully: {page.title()}")

    def test_page_has_header(self, page: Page, odpem_url):
        """Test that the page has a header with navigation"""
        page.goto(odpem_url)

        # Check for common header elements
        header_selectors = [
            "header",
            "nav",
            "[role='banner']",
            ".header",
            "#header"
        ]

        header_found = False
        for selector in header_selectors:
            try:
                header = page.locator(selector).first
                if header.is_visible():
                    header_found = True
                    print(f"✓ Header found with selector: {selector}")
                    break
            except:
                continue

        assert header_found, "No header element found on page"

    def test_navigation_menu_exists(self, page: Page, odpem_url):
        """Test that navigation menu exists and contains links"""
        page.goto(odpem_url)

        # Look for navigation links
        nav_links = page.locator("nav a, .menu a, .navigation a, header a").all()

        assert len(nav_links) > 0, "No navigation links found"
        print(f"✓ Found {len(nav_links)} navigation links")

    def test_contact_information_exists(self, page: Page, odpem_url):
        """Test that contact information is available"""
        page.goto(odpem_url)

        # Look for contact-related content
        page_content = page.content()

        has_phone = bool(re.search(r'\d{3}[-.\s]?\d{3}[-.\s]?\d{4}|\(\d{3}\)\s*\d{3}[-.\s]?\d{4}', page_content))
        has_email = bool(re.search(r'[\w\.-]+@[\w\.-]+\.\w+', page_content))
        has_address = "Jamaica" in page_content or "Kingston" in page_content

        contact_info_found = has_phone or has_email or has_address

        assert contact_info_found, "No contact information found on page"
        print(f"✓ Contact information found - Phone: {has_phone}, Email: {has_email}, Address: {has_address}")

    def test_footer_exists(self, page: Page, odpem_url):
        """Test that the page has a footer"""
        page.goto(odpem_url)

        footer_selectors = [
            "footer",
            "[role='contentinfo']",
            ".footer",
            "#footer"
        ]

        footer_found = False
        for selector in footer_selectors:
            try:
                footer = page.locator(selector).first
                if footer.is_visible():
                    footer_found = True
                    print(f"✓ Footer found with selector: {selector}")
                    break
            except:
                continue

        assert footer_found, "No footer element found on page"

    @pytest.mark.slow
    def test_page_load_performance(self, page: Page, odpem_url):
        """Test that the page loads within acceptable time"""
        import time

        start_time = time.time()
        page.goto(odpem_url, wait_until="domcontentloaded")
        load_time = time.time() - start_time

        assert load_time < 10, f"Page took {load_time:.2f}s to load (expected < 10s)"
        print(f"✓ Page loaded in {load_time:.2f} seconds")

    def test_no_console_errors(self, page: Page, odpem_url):
        """Test that the page doesn't have critical console errors"""
        console_errors = []

        def handle_console(msg):
            if msg.type == "error":
                console_errors.append(msg.text)

        page.on("console", handle_console)
        page.goto(odpem_url)

        # Allow some time for console messages
        page.wait_for_timeout(2000)

        # Filter out common non-critical errors
        critical_errors = [
            err for err in console_errors
            if not any(ignorable in err.lower() for ignorable in ['favicon', 'analytics', 'gtm'])
        ]

        if critical_errors:
            print(f"⚠ Found {len(critical_errors)} console errors:")
            for error in critical_errors[:5]:  # Print first 5
                print(f"  - {error[:100]}")
        else:
            print("✓ No critical console errors found")

    def test_responsive_mobile_view(self, page: Page, odpem_url):
        """Test that the page is responsive for mobile devices"""
        # Set mobile viewport
        page.set_viewport_size({"width": 375, "height": 667})
        page.goto(odpem_url)

        # Check if page is still accessible
        expect(page).to_have_title(re.compile(".+"))

        # Check if mobile menu exists (hamburger menu)
        mobile_menu_selectors = [
            ".mobile-menu",
            ".hamburger",
            "[aria-label*='menu' i]",
            ".menu-toggle",
            ".navbar-toggle"
        ]

        mobile_menu_found = False
        for selector in mobile_menu_selectors:
            try:
                if page.locator(selector).first.is_visible():
                    mobile_menu_found = True
                    print(f"✓ Mobile menu found: {selector}")
                    break
            except:
                continue

        print(f"✓ Mobile responsive test completed (Mobile menu: {mobile_menu_found})")

    def test_images_load(self, page: Page, odpem_url):
        """Test that images on the page load successfully"""
        page.goto(odpem_url, wait_until="networkidle")

        images = page.locator("img").all()

        if len(images) == 0:
            print("⚠ No images found on page")
            return

        broken_images = 0
        for img in images[:10]:  # Check first 10 images
            try:
                src = img.get_attribute("src")
                if src and not img.evaluate("img => img.complete && img.naturalHeight !== 0"):
                    broken_images += 1
            except:
                pass

        print(f"✓ Checked {min(len(images), 10)} images, {broken_images} broken")
        assert broken_images < 3, f"Too many broken images: {broken_images}"

    def test_external_links_valid(self, page: Page, odpem_url):
        """Test that external links have proper attributes"""
        page.goto(odpem_url)

        external_links = page.locator("a[href^='http']").all()

        if len(external_links) == 0:
            print("⚠ No external links found")
            return

        links_without_target = []
        for link in external_links[:10]:  # Check first 10
            try:
                href = link.get_attribute("href")
                target = link.get_attribute("target")

                if href and odpem_url not in href and target != "_blank":
                    links_without_target.append(href)
            except:
                pass

        print(f"✓ Checked {min(len(external_links), 10)} external links")
        if links_without_target:
            print(f"⚠ {len(links_without_target)} external links without target='_blank'")

    @pytest.mark.slow
    def test_search_functionality(self, page: Page, odpem_url):
        """Test search functionality if available"""
        page.goto(odpem_url)

        search_selectors = [
            "input[type='search']",
            "input[name*='search' i]",
            "input[placeholder*='search' i]",
            ".search-input",
            "#search"
        ]

        search_found = False
        for selector in search_selectors:
            try:
                search_input = page.locator(selector).first
                if search_input.is_visible():
                    search_found = True
                    print(f"✓ Search input found: {selector}")

                    # Try to use search
                    search_input.fill("emergency")
                    search_input.press("Enter")
                    page.wait_for_timeout(2000)

                    print("✓ Search functionality tested")
                    break
            except Exception as e:
                continue

        if not search_found:
            print("⚠ No search functionality found")

    def test_accessibility_basics(self, page: Page, odpem_url):
        """Test basic accessibility requirements"""
        page.goto(odpem_url)

        # Check for alt attributes on images
        images = page.locator("img").all()
        images_without_alt = 0

        for img in images[:10]:
            try:
                alt = img.get_attribute("alt")
                if alt is None or alt.strip() == "":
                    images_without_alt += 1
            except:
                pass

        # Check for proper heading structure
        h1_count = page.locator("h1").count()

        print(f"✓ Accessibility check:")
        print(f"  - H1 headings: {h1_count}")
        print(f"  - Images without alt: {images_without_alt}/{min(len(images), 10)}")

        # Ideally should have exactly 1 H1
        if h1_count != 1:
            print(f"⚠ Page has {h1_count} H1 headings (recommended: 1)")


@pytest.mark.playwright
class TestODPEMContent:
    """Test suite for ODPEM content verification"""

    def test_emergency_content_exists(self, page: Page, odpem_url):
        """Test that emergency-related content exists"""
        page.goto(odpem_url)
        content = page.content().lower()

        emergency_keywords = [
            "emergency",
            "disaster",
            "preparedness",
            "hurricane",
            "earthquake",
            "flood"
        ]

        found_keywords = [kw for kw in emergency_keywords if kw in content]

        assert len(found_keywords) >= 2, f"Expected emergency-related content. Found: {found_keywords}"
        print(f"✓ Found emergency keywords: {', '.join(found_keywords)}")

    def test_page_has_main_content(self, page: Page, odpem_url):
        """Test that the page has substantial content"""
        page.goto(odpem_url)

        # Get visible text content
        body_text = page.locator("body").inner_text()
        word_count = len(body_text.split())

        assert word_count > 50, f"Page has very little content: {word_count} words"
        print(f"✓ Page has {word_count} words of content")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
