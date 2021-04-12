# helix_survivae
Entry for the 24h game jam hosted on the Lazy-Developpers Discord server on April 10 2021

## How to use
#### to run it:
- Execute `helix_survivae.exe` in `./dist`

#### to modify it:
1. Open the repo in PyCharm
2. Delete the `./venv` folder
3. Let PyCharm re-create it with your own configuration, make sure to use **Python 3.9** or above
4. Install the `pip` dependencies:
    ```cmd
    pip install pyinstaller windows-curses
    ```
5. Run the program from a terminal using `python main.py`, as of the day of writing this, PyCharm's "run" terminal does not support Curses calls

note: I plan to port this to Pygcurses eventually, so the need to run in a separate terminal will be gone.

#### to compile it:
- run this command:
    ```cmd
        pyinstaller main.py --onefile --icon=icon.ico --name=helix_survivae
    ```

### TODO:
- ~~movement~~
- ~~character collisions~~
- ~~basic logic for placing stuff~~
- ~~health~~
- ~~enemies~~
- ~~enemy collisions~~
- loot + inventory
- ~~dynamic probability spawn randomizer~~
- ~~point system~~
- ~~main menu~~
- ~~pause menu~~
- ~~quit menu~~
- ~~saves~~
- ~~some way to destroy walls~~
- ~~cooldown on block breaking maybe?~~
- ~~warning for window not wide enough~~
 