// --- Stand A-Frame per Pannello Solare ed Elettronica ---
// Design ispirato alle foto richieste: Bracci laterali aperti, traversa,
// e un box centrale completamente protetto per contenere tutta l'elettronica.
//
// Componenti previsti: Arduino Uno, Waveshare Solar, LiPo, INA219, Modulino
// Orientamento di stampa: Lasciare il modello in questa posizione (Upright)! 
// Le pendenze a 45° permettono la stampa senza supporti (self-supporting).

// --- Parametri ---
panel_w = 90.5;
panel_l = 60.5;
panel_t = 3.0;
wall = 3.0;

// Dimensioni del box elettronico sigillato
box_w = 82;   // Larghezza esterna (76mm interni - perfetto per Arduino Uno/Waveshare)
box_l = 62;   // Lunghezza esterna (56mm interni)
box_d = 50;   // Profondità (47mm interni per impilare le schede)

leg_t = 6;    // Spessore dei bracci laterali

$fn = 60;

// --- Moduli 2D ---
// Profilo laterale dei bracci (triangolo rettangolo con scasso interno)
module leg_2d() {
    difference() {
        polygon(points=[
            [-75, 0],   // Punta anteriore a terra
            [65, 0],    // Base posteriore a terra
            [65, 140]   // Cima posteriore
        ]);
        
        // Scasso triangolare per creare l'effetto "frame"
        polygon(points=[
            [-40, 15],  
            [50, 15],   
            [50, 105]   
        ]);
    }
}

// --- Moduli 3D ---
module head_with_holes() {
    difference() {
        union() {
            // Vassoio frontale per il pannello
            translate([0, 0, -3])
                cube([panel_w + 2*wall, panel_l + 2*wall, 6], center=true);
                
            // Box Elettronica posteriore
            translate([0, 0, -6 - box_d/2])
                cube([box_w, box_l, box_d], center=true);
                
            // Torrette interne per le viti del coperchio
            for(x = [1, -1]) for(y = [1, -1]) {
                translate([x * (box_w/2 - wall - 3.5), y * (box_l/2 - wall - 3.5), -56])
                    cylinder(d=7, h=15);
            }
        }
        
        // Scasso frontale per inserire il pannello a filo
        translate([0, 0, -panel_t/2 + 0.1])
            cube([panel_w, panel_l, panel_t + 0.2], center=true);
            
        // Tacca inferiore per rimozione pannello
        translate([0, -panel_l/2, -panel_t/2])
            cube([15, 10, panel_t + 2], center=true);
            
        // Foro centrale passacavi dal pannello al box
        translate([0, 0, -10])
            cylinder(d=12, h=20, center=true);
            
        // Cavità interna del box (aperta sul retro Z=-56)
        translate([0, 0, -31 - 0.1])
            cube([box_w - 2*wall, box_l - 2*wall, 50.2], center=true);
            
        // Fori per le viti nel box
        for(x = [1, -1]) for(y = [1, -1]) {
            translate([x * (box_w/2 - wall - 3.5), y * (box_l/2 - wall - 3.5), -60])
                cylinder(d=2.5, h=20);
        }
        
        // Foro Piezo (laterale destro)
        translate([box_w/2, 0, -25])
            rotate([0, 90, 0])
            cylinder(d=10.5, h=20, center=true);
            
        // Foro Cavi Esterni (lato inferiore, punta verso il basso)
        translate([0, -box_l/2, -25])
            rotate([90, 0, 0])
            cylinder(d=8, h=20, center=true);
    }
}

module crossbar() {
    // Traversa posteriore di rinforzo tra i due bracci
    translate([0, 57.5, 7.5])
        cube([box_w + 2*leg_t, 15, 15], center=true);
}

module stand_assembly() {
    // La testa ruotata di 45 gradi
    translate([0, 0, 66.5])
        rotate([45, 0, 0])
        head_with_holes();
        
    // Braccio sinistro
    translate([-box_w/2 - leg_t, 0, 0])
        rotate([90, 0, 90])
        linear_extrude(leg_t)
        leg_2d();
        
    // Braccio destro
    translate([box_w/2, 0, 0])
        rotate([90, 0, 90])
        linear_extrude(leg_t)
        leg_2d();
        
    crossbar();
}

module back_lid() {
    // Coperchio posteriore di chiusura del box
    difference() {
        cube([box_w, box_l, 3], center=true);
        
        // Fori viti con svasatura
        for(x = [1, -1]) for(y = [1, -1]) {
            translate([x * (34.5), y * (24.5), -5])
                cylinder(d=3.2, h=10);
            translate([x * (34.5), y * (24.5), 0])
                cylinder(d=6.0, h=5);
        }
        
        // Griglia di aerazione
        for(x = [-20 : 20 : 20]) {
            for(y = [-15 : 15 : 15]) {
                translate([x, y, -5])
                    cylinder(d=4, h=10, $fn=20);
            }
        }
    }
}

// --- RENDER ---

// Struttura Principale (Vassoio + Bracci)
stand_assembly();

// Coperchio Posteriore (spostato a lato per la stampa)
translate([120, 0, 1.5])
    back_lid();
