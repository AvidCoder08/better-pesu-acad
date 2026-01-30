from pesuacademy import PESUAcademy
import getpass
import asyncio
f = open('result.txt' \
'')
async def main():
    """
    Login to PESU Academy and retrieve profile details
    """
    print("=" * 50)
    print("PESU Academy Login & Profile Viewer")
    print("=" * 50)
    
    # Get credentials from user
    username = input("\nEnter your PRN/SRN: ").strip()
    password = getpass.getpass("Enter your password: ")
    
    # Create PESUAcademy instance
    print("\nConnecting to PESU Academy...")
    
    try:
        # Login - this is a class method that returns an authenticated instance
        print("Logging in...")
        pesu = await PESUAcademy.login(username, password)
        
        print("✓ Login successful!\n")
        
        # Get profile details
        print("Fetching profile details...\n")
        profile = await pesu.get_profile()
        
        # Display profile information
        print("=" * 50)
        print("PROFILE DETAILS")
        print("=" * 50)
        
        # Profile is a Pydantic model, convert to dict for display
        if hasattr(profile, 'model_dump'):
            profile_dict = profile.model_dump()
        elif hasattr(profile, 'dict'):
            profile_dict = profile.dict()
        else:
            profile_dict = vars(profile)
        
        for key, value in profile_dict.items():
            # Format the key to be more readable
            formatted_key = key.replace('_', ' ').title()
            print(f"{formatted_key}: {value}")
        
        print("=" * 50)
        
        # Close the session
        await pesu.close()
        print("\nSession closed.")
        
    except Exception as e:
        print(f"✗ An error occurred: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())