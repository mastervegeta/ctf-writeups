import java.util.*;
import javax.crypto.Cipher;
import javax.crypto.spec.SecretKeySpec;
import java.security.*;

class VaultDoor8 {

    public static void main(String args[]) {
        Scanner scanner = new Scanner(System.in);
        reverse_checkPassword();
        System.out.print("Enter vault password: ");
        String userInput = scanner.next();
        String input = userInput.substring(8, userInput.length() - 1);

        VaultDoor8 vaultDoor = new VaultDoor8();
        if (vaultDoor.checkPassword(input)) {
            System.out.println("Access granted.");
        } else {
            System.out.println("Access denied!");
        }
    }

    /* Scramble a password by transposing pairs of bits. */
    public char[] scramble(String password) {
        char[] chars = password.toCharArray();
        System.out.println("Scrambling password: " + password);

        for (int i = 0; i < chars.length; i++) {
            char c = chars[i];

            c = switchBits(c, 1, 2);
            c = switchBits(c, 0, 3);
            /*
             * c = switchBits(c,14,3);
             * c = switchBits(c, 2, 0);
             */
            c = switchBits(c, 5, 6);
            c = switchBits(c, 4, 7);
            c = switchBits(c, 0, 1);
            /* now this makes original 0 -> 3 -> 2, so now index 0 is 2 */

            /*
             * d = switchBits(d, 4, 5);
             * e = switchBits(e, 5, 6);
             */
            c = switchBits(c, 3, 4);
            c = switchBits(c, 2, 5);
            c = switchBits(c, 6, 7);

            chars[i] = c;
        }

        return chars;
    }

    /*
     * Move the bit in position p1 to position p2, and move the bit
     * that was in position p2 to position p1. Precondition: p1 < p2
     */
    public char switchBits(char c, int p1, int p2) {
        char mask1 = (char) (1 << p1);
        char mask2 = (char) (1 << p2);
        /*
         * char mask3 = (char)(1<<p1<<p2);
         * mask1++;
         * mask1--;
         */

        char bit1 = (char) (c & mask1);
        char bit2 = (char) (c & mask2);
        /*
         * System.out.println("bit1 " + Integer.toBinaryString(bit1));
         * System.out.println("bit2 " + Integer.toBinaryString(bit2));
         */

        char rest = (char) (c & ~(mask1 | mask2));
        char shift = (char) (p2 - p1);

        char result = (char) ((bit1 << shift) | (bit2 >> shift) | rest);
        return result;
    }

    public boolean checkPassword(String password) {
        char[] scrambled = scramble(password);
        char[] expected = {
                0xF4, 0xC0, 0x97, 0xF0, 0x77, 0x97, 0xC0, 0xE4,
                0xF0, 0x77, 0xA4, 0xD0, 0xC5, 0x77, 0xF4, 0x86,
                0xD0, 0xA5, 0x45, 0x96, 0x27, 0xB5, 0x77, 0xF1,
                0xC2, 0xD2, 0x95, 0xD0, 0xF0, 0x94, 0xF1, 0x95
        };
        return Arrays.equals(scrambled, expected);
    }

    public char[] reverse_scramble(String password) {
        char[] chars = password.toCharArray();
        System.out.println("Scrambling password: " + password);

        for (int i = 0; i < chars.length; i++) {
            char c = chars[i];

            c = switchBits(c, 6, 7);
            c = switchBits(c, 2, 5);
            c = switchBits(c, 3, 4);

            c = switchBits(c, 0, 1);
            c = switchBits(c, 4, 7);
            c = switchBits(c, 5, 6);

            c = switchBits(c, 0, 3);
            c = switchBits(c, 1, 2);

            /*
             * c = switchBits(c,14,3);
             * c = switchBits(c, 2, 0);
             */

            /* now this makes original 0 -> 3 -> 2, so now index 0 is 2 */

            /*
             * d = switchBits(d, 4, 5);
             * e = switchBits(e, 5, 6);
             */

            chars[i] = c;
        }

        return chars;
    }

    public static void reverse_checkPassword() {

        char[] expected = {
                0xF4, 0xC0, 0x97, 0xF0, 0x77, 0x97, 0xC0, 0xE4,
                0xF0, 0x77, 0xA4, 0xD0, 0xC5, 0x77, 0xF4, 0x86,
                0xD0, 0xA5, 0x45, 0x96, 0x27, 0xB5, 0x77, 0xF1,
                0xC2, 0xD2, 0x95, 0xD0, 0xF0, 0x94, 0xF1, 0x95
        };
        String expected_in_string = new String(expected);

        char[] unscrambled = reverse_scramble(expected_in_string);

        // return Arrays.equals(unscrambled, expected);
    }

}