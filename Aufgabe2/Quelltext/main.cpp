// ===========================
// Aufgabe:      Spießgesellen
// Author:       Elia Doumerc
// Teilnahme-ID: 55627
// Datum:        2021-02
// ===========================

#include "Graph.h"
#include "Zeit.h"
#include <boost/program_options.hpp>
#include <iostream>

using namespace std;
using namespace boost::program_options;

int main(int argc, char **argv){
    
    // Legt alle Programmoptionen fest.
    options_description desc("Erlaubte Optionen");
    desc.add_options()
        ("help,h", "Erstellt diese Ausgabe")
        ("file,f", value<string>()->required(), "Die Datei mit der Eingabeinformation")
        ("verbose,v", "Erstellt die verbose Ausgabe.")
        ("zeit,z", value<string>()->default_value(""), "Ausgabedatei für Benchmarks. Werden standardmäßig nicht ausgegeben.")
        ("mehrere,m", "Erlaubt das Vorkommen einer Obstsorte in mehreren Schüsseln. Für die korrekte Funktionsweise " 
                      "muss in der Eingabedatei die Schüsselzahl in eine neue Zeile unter die Sortenzahl geschrieben werden.")
    ;
    // Optionen, die nicht als Variablen geschrieben werden müssen (--option=wert)
    positional_options_description pod;
    pod.add("file", 1);

    variables_map vm;
    try {
        // parse arguments
        store(command_line_parser(argc, argv).options(desc).positional(pod).run(), vm);
        // check arguments
        notify(vm);
    }
    catch (std::exception& e) {
        // Falls nicht --help geschrieben wurde, drucke Fehler
        if (!vm.count("help")) {
            //cout << "Error: " << e.what() << endl;
            cout << "Fehler: Falsche Eingabe\n";
        }
        // Drucke Hilfe
        cout << "Nutzung: Aufgabe2 Eingabedatei [Optionen]\n";
        cout << desc << endl;
        return 1;
    }

    string dateiname = vm["file"].as< string >();
    bool verbose = vm.count("verbose"); 
    bool mehr_schuesseln = vm.count("mehrere");
    string outfile = vm["zeit"].as< string >();
    
    // Für die Zeitmessung
    Messer M(outfile, dateiname);
    if (!outfile.size()) M.print_result = false;
    
    M.add_tmstmp("Dateieinlesung");
    
    //========= Programmlogik ===========
    // Öffne die Datei und lese die Daten Zeile für Zeile ein.
    if(verbose) cout << "Öffne die Datei " << dateiname << "...\n";
    ifstream datei(dateiname); // inputFileStream (Konstruktor) 2.Argument ist standardmäßig "in"
    if (!datei.is_open()){
        cout << "Datei konnte nicht geöffnet werden.\n";
        return 1;
    }
    
    string zeile, zeile2;
    // 1. Obstsortenzahl (Obergrenze)
    getline(datei, zeile);
    ushort n_sorten = stoi(zeile); // wandelt sie in einen Integer um.
    
    // Erweiterung 
    ushort n_schuesseln = n_sorten;
    if (mehr_schuesseln) {
        getline(datei, zeile);
        n_schuesseln = stoi(zeile);
    }
    
    M.add_tmstmp("Konstruktor");
    Graph G(n_sorten, n_schuesseln); // Erstelle den Graphen mit der Sortenzahl
    
    M.add_tmstmp("Preferenzen");
    // 2. Wunschsorten
    getline(datei, zeile);
    G.setze_preferenzen(&zeile);
    
    M.add_tmstmp("Spießverarbeitung");
    // 3. n_spiesse und 2N. spiesse, schüsseln
    getline(datei, zeile);
    int n_spiesse = stoi(zeile);
    for (int i=0; i<n_spiesse; i++)
    {
        getline(datei, zeile);
        getline(datei, zeile2);
        try{
            G.add_spiess(&zeile, &zeile2); // Verarbeitet den Spieß und setzt ihn in Kanten ein.
        } catch (string x){
            cout << "Der Name " << x << " ist für eine Schüssel ungültig.\n";
            return 1;
        }
        
    }
    datei.close();
    
    if (mehr_schuesseln){
        M.add_tmstmp("eliminiere_Kanten_2");
        G.eliminiere_kanten2();
    }
    
    M.add_tmstmp("Ausgabe"); // Zeit
    if(verbose) G.drucke_resultate_v();
    else G.drucke_resultate();
    
    return 0;
}