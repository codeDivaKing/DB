from collections import Counter
class Solution:
    def __init__(self):
        pass
    def find_word_with_anagram(self, words, s):
        s_counter = Counter(s)
        for word in words:
            w_counter = Counter(word)
            if all(s_counter[ch] >= w_counter[ch] for ch in w_counter):
                return word
        return None



def main():
    sol = Solution()
    words = ["cat", "baby", "bird", "fruit"]
    print(sol.find_word_with_anagram(words, "tacjbcebef"))  # cat
    print(sol.find_word_with_anagram(words, "bacdrigb"))    # bird

if __name__ == "__main__":
    main()
