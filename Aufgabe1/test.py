from os import system
for i in range(1, 8):
	print(f"python3 Aufgabe1.py Beispieleingaben/flohmarkt{i}.txt -o Ausgabe/out{i}.txt -s s-e-l -h bssf -h blsf")
	system(f"python3 Aufgabe1.py Beispieleingaben/flohmarkt{i}.txt -o Ausgabe/out{i}.txt -s s-e-l -h bssf -h blsf")
